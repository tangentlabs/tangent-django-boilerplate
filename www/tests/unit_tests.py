from django.contrib.auth import models


def test_for_smoke():
    user = models.User(first_name='Barry',
                       last_name='Chuckle')
    assert 'Barry' == user.get_short_name()
