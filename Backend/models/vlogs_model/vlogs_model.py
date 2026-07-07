from django.db import models
from Backend.models.base_user_model.base_model import TimeManager,User

class Vlogs(TimeManager):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vlog_title = models.CharField(max_length=500)
    text = models.TextField()

    url = models.URLField(max_length=230)
    media = models.FileField(upload_to='media/')
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.vlog_title},{self.created_at}"