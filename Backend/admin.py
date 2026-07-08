from django.contrib import admin

from Backend.models.base_user_model.base_model import User
from Backend.models.comments_model.news_coment import NewsComment
from Backend.models.comments_model.vlogs_coment import VlogsComment
from Backend.models.games_model.games_model import Games, GamePlatformRelease, Platform
from Backend.models.news_model.news_model import News
from Backend.models.vlogs_model.vlogs_model import Vlogs

admin.site.register([User, News, NewsComment, Vlogs, VlogsComment, Games, GamePlatformRelease, Platform])