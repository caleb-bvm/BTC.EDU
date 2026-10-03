import re
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.utils.http import content_disposition_header


def file_response(request, asset, download=False):
    """Call only after context authorization. Never exposes storage paths."""
    root = Path(settings.MEDIA_ROOT).resolve()
    try:
        path = Path(asset.file.path).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size != asset.size:
            raise Http404("El archivo no está disponible. Contacta al creador.")
    except (OSError, ValueError) as exc:
        raise Http404("El archivo no está disponible.") from exc
    size = asset.size
    etag = f'"{asset.sha256}"'
    start, end, status = 0, size - 1, 200
    requested_range = request.headers.get("Range")
    if requested_range and request.headers.get("If-Range", etag) == etag:
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested_range)
        try:
            if not match or not any(match.groups()):
                raise ValueError
            left, right = match.groups()
            if left:
                start = int(left)
                end = min(int(right), size - 1) if right else size - 1
            else:
                suffix = int(right)
                if suffix <= 0:
                    raise ValueError
                start = max(0, size - suffix)
            if start > end or start >= size:
                raise ValueError
        except ValueError:
            response = HttpResponse(status=416)
            response["Content-Range"] = f"bytes */{size}"
            response["Cache-Control"] = "private, no-store"
            return response
        status = 206
    if request.headers.get("If-None-Match") == etag and status == 200:
        response = HttpResponse(status=304)
    elif request.method == "HEAD":
        response = HttpResponse(status=status, content_type=asset.mime_type)
    else:
        try:
            handle = path.open("rb")
        except OSError as exc:
            raise Http404("El archivo no está disponible.") from exc

        def chunks():
            with handle:
                handle.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = handle.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        response = StreamingHttpResponse(chunks(), status=status, content_type=asset.mime_type)
        response._resource_closers.append(handle.close)
    response["ETag"] = etag
    response["Accept-Ranges"] = "bytes"
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = content_disposition_header(download or asset.kind == "material", asset.original_name)
    if response.status_code != 304:
        response["Content-Length"] = end - start + 1
    if status == 206:
        response["Content-Range"] = f"bytes {start}-{end}/{size}"
    return response
