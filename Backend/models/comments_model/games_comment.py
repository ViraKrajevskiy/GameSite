from django.db import models
from Backend.models.base_user_model.base_model import TimeManager, User

class GamesComment(TimeManager):
    games_news = models.ForeignKey('Games', on_delete=models.CASCADE, related_name='games_comments')
    games_comment_writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_user')
    games_text = models.CharField(max_length=400)

    def __str__(self):
        return f"{self.games_comment_writer}: {self.games_text[:50]} {self.created_at}"