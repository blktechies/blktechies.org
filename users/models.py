from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserAlternateEmail(models.Model):
    STATUS_OK = 0
    STATUS_NEEDS_VERIFY = 1
    STATUS_SPAM = 2
    STATUS_BANNED = 3
    STATUS_CHOICES = (
        (STATUS_OK, 'active'),
        (STATUS_NEEDS_VERIFY, 'not verified'),
        (STATUS_SPAM, 'spam'),
        (STATUS_BANNED, 'banned'),
        (STATUS_INACTIVE, 'inactive'),
        (STATUS_DELETED, 'deleted'),
    )

    id = models.AutoField(primary_key=True)
    email = models.EmailField(db_index=True, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_add_now=True)
    verified_at = models.DateTimeField(blank=True)

    class Meta(object):
        index_together = (
            ('user', 'status'),
        )
