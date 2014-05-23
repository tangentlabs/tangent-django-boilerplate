from django.contrib.auth import models
import pytest


@pytest.mark.django_db
def test_database_access():
    models.User.objects.create_user(
        'egg', 'egg@box.com', 'yolk')
