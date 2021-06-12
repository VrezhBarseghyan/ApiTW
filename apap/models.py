from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)

    REQUIRED_FIELDS = []

    def user_id(self):
        return self.id.__str__()

class Post(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=255)
    likes = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
