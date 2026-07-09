from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from Backend.models.base_user_model.base_model import TimeManager, User


class GamesRating(TimeManager):
    game = models.ForeignKey('Games', on_delete=models.CASCADE, related_name='ratings')
    rating_writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_ratings')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        unique_together = ('game', 'rating_writer')

    def __str__(self):
        return f"{self.rating}/10 — {self.game.title} ({self.rating_writer.username})"