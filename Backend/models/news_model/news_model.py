from django.db import models
from Backend.models.base_user_model.base_model import TimeManager, User

class News(TimeManager):
    title = models.CharField(max_length=230)
    content = models.TextField()
    url = models.URLField(max_length=230)
    media = models.FileField(upload_to='media/')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'{self.title}  {self.created_at}'