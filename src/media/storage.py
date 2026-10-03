from django.core.files.storage import FileSystemStorage


class PrivateStorage(FileSystemStorage):
    def url(self, name):
        raise ValueError("Los archivos requieren una ruta autorizada.")


private_storage = PrivateStorage()
