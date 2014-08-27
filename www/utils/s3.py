"""
Custom storage classes to allows statics and media to be stored
with prefixed keys in S3.

See http://tartarus.org/james/diary/2013/07/18/fun-with-django-storage-backends
"""
from storages.backends.s3boto import S3BotoStorage


class StaticRootS3BotoStorage(S3BotoStorage):
    location = 'static'


class MediaRootS3BotoStorage(S3BotoStorage):
    location = 'media'
