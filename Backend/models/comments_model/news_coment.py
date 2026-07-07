from django.db import models
from Backend.models.base_user_model.base_model import TimeManager, User

class NewsComment(TimeManager):
    news = models.ForeignKey('News', on_delete=models.CASCADE, related_name='comments')
    comment_writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='newscomments')
    text = models.CharField(max_length=400)

    def __str__(self):
        return f"{self.comment_writer}: {self.text[:50]} {self.created_at}"