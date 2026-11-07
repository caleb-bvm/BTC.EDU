"""Private uploaded assets with validated type, size and SHA-256."""
import hashlib
import uuid
from pathlib import PurePosixPath

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext

from content.immutability import FrozenRecord

from .storage import private_storage


def private_name(instance, filename):
    """Random storage name under assets/ that keeps only the lowercase extension."""
    return f"assets/{uuid.uuid4().hex}{PurePosixPath(filename).suffix.lower()}"


def validate_mp4_boxes(upload):
    """Check that an MP4 upload has a valid top-level box structure."""
    offset, boxes = 0, set()
    while offset < upload.size:
        upload.seek(offset)
        header = upload.read(16)
        if len(header) < 8:
            raise ValidationError(gettext("El archivo MP4 está incompleto."))
        size = int.from_bytes(header[:4], "big")
        minimum = 8
        if size == 1:
            if len(header) < 16:
                raise ValidationError(gettext("El archivo MP4 está incompleto."))
            size, minimum = int.from_bytes(header[8:16], "big"), 16
        elif size == 0:
            size = upload.size - offset
        if size < minimum or offset + size > upload.size:
            raise ValidationError(gettext("El archivo MP4 está incompleto o tiene un contenedor inválido."))
        boxes.add(header[4:8])
        offset += size
    upload.seek(0)
    if not {b"ftyp", b"moov", b"mdat"}.issubset(boxes):
        raise ValidationError(gettext("El MP4 requiere índice y datos completos; no admite fragmentos sueltos."))


def inspect_upload(upload):
    """Validate size and content and return the asset kind and MIME type.

    The extension must match the bytes.
    """
    extension = PurePosixPath(upload.name.replace("\\", "/")).suffix.lower()
    if not upload.size or upload.size > settings.CONTENT_MAX_UPLOAD_BYTES:
        raise ValidationError(gettext("El archivo está vacío o supera el límite de carga."))
    upload.seek(0)
    head = upload.read(4096)
    upload.seek(max(0, upload.size - 1024))
    tail = upload.read(1024)
    upload.seek(0)
    if extension == ".mp4" and len(head) >= 24 and head[4:8] == b"ftyp" and 16 <= int.from_bytes(head[:4], "big") <= upload.size:
        validate_mp4_boxes(upload)
        kind, mime = "video", "video/mp4"
    elif extension == ".pdf" and head.startswith(b"%PDF-") and b"%%EOF" in tail:
        kind, mime = "material", "application/pdf"
    elif extension in (".txt", ".vtt"):
        import codecs
        decoder = codecs.getincrementaldecoder("utf-8")()
        try:
            for chunk in upload.chunks():
                decoded = decoder.decode(chunk)
                if any(ord(char) < 32 and char not in "\n\r\t" for char in decoded):
                    raise ValidationError(gettext("El texto contiene caracteres de control."))
            decoder.decode(b"", final=True)
        except UnicodeDecodeError as exc:
            raise ValidationError(gettext("El texto debe estar codificado en UTF-8.")) from exc
        finally:
            upload.seek(0)
        if extension == ".vtt" and not head.removeprefix(b"\xef\xbb\xbf").startswith((b"WEBVTT\n", b"WEBVTT\r\n")):
            raise ValidationError(gettext("El subtítulo debe tener formato WebVTT."))
        kind, mime = ("subtitle", "text/vtt") if extension == ".vtt" else ("material", "text/plain")
    else:
        raise ValidationError(gettext("Formato no admitido o contenido incompatible. Usa MP4, PDF, TXT o VTT."))
    declared = getattr(upload, "content_type", None)
    if declared and declared not in (mime, "application/octet-stream"):
        raise ValidationError(gettext("El tipo declarado no coincide con el contenido."))
    return kind, mime


class Asset(FrozenRecord):
    """Immutable private file with its detected kind, MIME type, size and SHA-256."""
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="propietario")
    file = models.FileField("archivo privado", storage=private_storage, upload_to=private_name)
    original_name = models.CharField(max_length=200, editable=False)
    kind = models.CharField(max_length=12, editable=False)
    mime_type = models.CharField(max_length=80, editable=False)
    size = models.PositiveBigIntegerField(editable=False)
    sha256 = models.CharField(max_length=64, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "archivo privado"
        verbose_name_plural = "archivos privados"

    def __str__(self):
        return f"{self.original_name} ({self.size} bytes)"

    def clean(self):
        if self._state.adding and self.file:
            if self.file._committed:
                raise ValidationError({"file": gettext("Carga un archivo nuevo; no se aceptan rutas de disco.")})
            self.kind, self.mime_type = inspect_upload(self.file.file)
            self.original_name = PurePosixPath(self.file.name.replace("\\", "/")).name[:200]
            self.original_name = "".join(char for char in self.original_name if ord(char) >= 32)
            self.size = self.file.size
            digest = hashlib.sha256()
            for chunk in self.file.chunks():
                digest.update(chunk)
            self.sha256 = digest.hexdigest()
            self.file.seek(0)

    def save(self, *args, **kwargs):
        # Metadata is derived before field validation; subsequent changes are rejected.
        if self._state.adding:
            self.clean()
        return super().save(*args, **kwargs)


COVER_SIZE = (1600, 900)
COVER_MAX_BYTES = 8 * 1024 * 1024


def cover_name(instance, filename):
    """Random storage name under covers/; the uploaded name is not kept."""
    return f"covers/{uuid.uuid4().hex}.webp"


def normalize_cover(upload):
    """Rebuild a JPG, PNG or WebP upload as a 1600×900 WebP without its metadata.

    The image is centred and cropped to 16:9, so the catalog never shows bands or distortion.
    """
    import warnings
    from io import BytesIO

    from django.core.files.base import ContentFile
    from PIL import Image, ImageOps, UnidentifiedImageError

    if not upload or not upload.size or upload.size > COVER_MAX_BYTES:
        raise ValidationError(gettext("Elige una imagen JPG, PNG o WebP de hasta 8 MB."))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            upload.seek(0)
            with Image.open(upload) as source:
                if source.format not in ("JPEG", "PNG", "WEBP") or getattr(source, "is_animated", False):
                    raise ValidationError(gettext("Usa una imagen JPG, PNG o WebP sin animación."))
                if source.width * source.height > 40_000_000:
                    raise ValidationError(gettext("La imagen no debe superar 40 megapíxeles."))
                source.load()
                rotated = ImageOps.exif_transpose(source)
                if rotated.width < 800 or rotated.height < 450:
                    raise ValidationError(gettext("La imagen debe medir al menos 800 × 450 píxeles."))
                # New pixels only: EXIF, GPS, comments and colour profiles are discarded.
                rgba = rotated.convert("RGBA")
                pixels = Image.new("RGB", rgba.size, "white")
                pixels.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
                cover = ImageOps.fit(pixels, COVER_SIZE, Image.Resampling.LANCZOS)
                output = BytesIO()
                cover.save(output, format="WEBP", quality=82, method=4)
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValidationError(gettext("No pudimos leer la imagen. Elige otro archivo JPG, PNG o WebP.")) from exc
    finally:
        upload.seek(0)
    return ContentFile(output.getvalue(), name="portada.webp")


class Cover(FrozenRecord):
    """Normalized course cover; public only once a published version uses it."""
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="propietario")
    file = models.FileField("imagen", storage=private_storage, upload_to=cover_name)
    size = models.PositiveIntegerField(editable=False)
    sha256 = models.CharField(max_length=64, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "portada"
        verbose_name_plural = "portadas"

    def __str__(self):
        return f"portada {self.pk}"

    @classmethod
    def from_upload(cls, creator, upload):
        """Unsaved cover built from an upload; raises ValidationError if it is not a usable image."""
        image = normalize_cover(upload)
        data = image.read()
        image.seek(0)
        return cls(creator=creator, file=image, size=len(data), sha256=hashlib.sha256(data).hexdigest())
