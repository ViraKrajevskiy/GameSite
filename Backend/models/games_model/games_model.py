from django.db import models
from Backend.models.base_user_model.base_model import TimeManager


class Games(TimeManager):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    url = models.URLField()
    platforms = models.ManyToManyField('Platform', through='GamePlatformRelease', related_name='games')

    def __str__(self):
        return f'{self.title}, {self.created_at}'


class Platform(TimeManager):
    title = models.CharField(max_length=100)      # Steam, itch.io, GOG...
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.title


class GamePlatformRelease(TimeManager):
    STATUS_CHOICES = [
        ('released', 'Released'),
        ('waiting', 'Waiting release'),
        ('not_released', 'Not released'),
    ]

    game = models.ForeignKey(Games, on_delete=models.CASCADE, related_name='platform_releases')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='game_releases')
    url_platform = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_released')
    release_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('game', 'platform')

    def __str__(self):
        return f'{self.game.title} — {self.platform.title} ({self.status})'