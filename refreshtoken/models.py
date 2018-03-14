import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Prior to Django 1.5, the AUTH_USER_MODEL setting does not exist.
# Note that we don't perform this code in the compat module due to
# bug report #1297
# See: https://github.com/tomchristie/django-rest-framework/issues/1297
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class RefreshToken(models.Model):
    """
    Copied from
    https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/authtoken/models.py
    Wanted to only change the user relation to be a "ForeignKey" instead of a OneToOneField

    The `ForeignKey` value allows us to create multiple RefreshTokens per user

    """  # noqa
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='refresh_tokens',
        on_delete=models.CASCADE,
    )
    app = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'app')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(RefreshToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def revoke(self):
        self.delete()
        return self.__class__.objects.create(user=self.user, app=self.app)

    def __str__(self):
        return self.key

    def __repr__(self):
        return 'RefreshToken(pk=%r, key=%r, user=%r, app=%r, created=%r)' % (
            self.pk,
            self.key,
            getattr(self, 'user', None),
            self.app,
            self.created,
        )
