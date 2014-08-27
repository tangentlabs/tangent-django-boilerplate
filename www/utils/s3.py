"""
Custom storage classes to allows statics and media to be stored
with prefixed keys in S3.

See http://tartarus.org/james/diary/2013/07/18/fun-with-django-storage-backends
"""
from django.core.files.storage import get_storage_class

from storages.backends.s3boto import S3BotoStorage


# Copied from http://django-compressor.readthedocs.org/en/latest/remote-storages/#using-staticfiles
class StaticRootS3BotoStorage(S3BotoStorage):
    location = 'static'

    def __init__(self, *args, **kwargs):
        super(StaticRootS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(StaticRootS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name


class MediaRootS3BotoStorage(S3BotoStorage):
    location = 'media'
