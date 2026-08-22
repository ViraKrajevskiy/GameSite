from django.db import models
from Backend.models.base_user_model.base_model import TimeManager, User

class NewsComment(TimeManager):
    news = models.ForeignKey('News', on_delete=models.CASCADE, related_name='comments')
    comment_writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='newscomments')
    text = models.CharField(max_length=400)
    # Ответ на другой комментарий этой же новости. Дальше 1 уровня не идём:
    # если пользователь отвечает на реплай — сериализатор ставит parent = parent.parent,
    # а сам текст начинается с «@username, ...». См. serializers.
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies',
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.comment_writer}: {self.text[:50]} {self.created_at}"