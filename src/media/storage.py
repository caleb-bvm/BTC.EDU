"""File storage outside the public static and media URLs."""
from django.core.files.storage import FileSystemStorage


class PrivateStorage(FileSystemStorage):
    """Filesystem storage that never builds URLs.

    Files are served by media.delivery after authorization.
    """
    def url(self, name):
        raise ValueError("Los archivos requieren una ruta autorizada.")


private_storage = PrivateStorage()
