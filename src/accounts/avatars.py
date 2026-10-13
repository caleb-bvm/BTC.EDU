"""Private, normalized profile images; uploaded bytes are never served directly."""
import logging
import warnings
from io import BytesIO
from pathlib import PurePosixPath
from uuid import uuid4

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


def normalize_avatar(upload, crop_x=50, crop_y=50, zoom=1):
    if not upload or upload.size > 3 * 1024 * 1024:
        raise ValidationError("Elige una foto JPG, PNG o WebP de hasta 3 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(upload) as source:
                if source.format not in ("JPEG", "PNG", "WEBP") or getattr(source, "is_animated", False):
                    raise ValidationError("Usa una foto JPG, PNG o WebP sin animación.")
                if source.width * source.height > 16_000_000 or min(source.size) < 64:
                    raise ValidationError("La foto debe medir al menos 64 píxeles por lado y no superar 16 megapíxeles.")
                source.load()
                rotated = ImageOps.exif_transpose(source)
                # Rebuild pixels, discarding EXIF, GPS, comments and source metadata.
                rgba = rotated.convert("RGBA")
                pixels = Image.new("RGB", rgba.size, "white")
                pixels.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
                edge = min(pixels.size) / float(zoom)
                left = (pixels.width - edge) * float(crop_x) / 100
                top = (pixels.height - edge) * float(crop_y) / 100
                thumbnail = pixels.crop((left, top, left + edge, top + edge)).resize((384, 384), Image.Resampling.LANCZOS)
                output = BytesIO()
                thumbnail.save(output, format="WEBP", quality=85, method=4)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValidationError("No pudimos leer la foto. Elige otro archivo JPG, PNG o WebP.") from exc
    return ContentFile(output.getvalue(), name=f"{uuid4().hex}.webp")


@transaction.atomic
def update_avatar(user, image=None, remove=False):
    from django.db.models import F

    from .models import User
    User.objects.filter(pk=user.pk).update(profile_public=F("profile_public"))
    member = User.objects.get(pk=user.pk)
    if image and (not member.is_active or member.get_session_auth_hash() != user.get_session_auth_hash()):
        raise PermissionDenied("Tu cuenta cambió. Vuelve a entrar antes de guardar la foto.")
    old_name, storage = member.avatar.name, member.avatar.storage
    new_name = ""
    try:
        if image:
            member.avatar.save(image.name, image, save=False)
            new_name = member.avatar.name
        elif remove:
            member.avatar = ""
        else:
            return member
        member.save(update_fields=("avatar",))
    except Exception:
        if new_name:
            storage.delete(new_name)
        raise
    if old_name and old_name != member.avatar.name:
        def remove_old():
            try:
                storage.delete(old_name)
            except OSError:
                # A Windows reader may briefly hold the old file. Its URL is
                # already revoked; maintenance retries cleanup without undoing
                # the committed profile change or reporting a false save failure.
                logger.warning("Old profile photo cleanup deferred for account %s.", member.pk)
        transaction.on_commit(remove_old)
    user.avatar = member.avatar.name
    return member


def avatar_visible(actor, member):
    if not member.is_active:
        return False
    if actor == member or member.has_public_profile:
        return True
    if member.account_type != "student":
        return False
    if not actor.is_authenticated or not actor.is_active or actor.account_type not in ("student", "creator"):
        return False
    from django.db.models import Q

    from learning.models import CommunityPost, LessonQuestion
    if actor.account_type == "creator":
        profile = getattr(actor, "creator_profile", None)
        if not profile or profile.status != "approved":
            return False
        return CommunityPost.objects.filter(author=member, hidden=False, version__course__creator=actor).exists() or LessonQuestion.objects.filter(enrollment__student=member, enrollment__version__course__creator=actor).exists()
    return CommunityPost.objects.filter(author=member, hidden=False).filter(
        Q(version__enrollment__student=actor) | Q(version__course__creator=actor)
    ).exists()


def avatar_token(member):
    return PurePosixPath(member.avatar.name).stem if member.avatar else ""
