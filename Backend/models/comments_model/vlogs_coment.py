from django.db import models
from Backend.models.base_user_model.base_model import TimeManager


class VlogsComment(TimeManager):
    vlogs = models.ForeignKey('Vlogs', on_delete=models.CASCADE, related_name='vlogs_comments')
    comment = models.CharField(max_length=1200)
    vl_comment_author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='vl_comment_author')

    def __str__(self):
        return f"{self.comment}{self.vl_comment_author}{self.created_at}"