"""
Проверки загружаемых файлов.

Понадобились после того, как контент стало можно создавать через API:
раньше писать могла только админка, теперь это делает роль 'creator',
а значит любой файл приходит снаружи. Без ограничений можно было залить
что угодно и любого размера — включая .html и .svg, которые Django в
режиме DEBUG отдаёт из MEDIA_ROOT как есть, то есть со скриптами внутри.
"""
from django.core.exceptions import ValidationError

MB = 1024 * 1024

# Картинки: обложки игр, аватары
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
IMAGE_MAX_SIZE = 5 * MB

# Медиа новостей и влогов — картинки плюс видео
VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'm4v'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
MEDIA_MAX_SIZE = 50 * MB

# Эти расширения браузер выполняет — в общей папке медиа им не место
DANGEROUS_EXTENSIONS = {
    'html', 'htm', 'svg', 'xml', 'js', 'mjs',
    'php', 'phtml', 'py', 'sh', 'bat', 'cmd', 'exe', 'dll', 'jar',
}


def _extension(name):
    return name.rsplit('.', 1)[-1].lower() if '.' in name else ''


def _human(size):
    return f'{size / MB:.0f} МБ'


def _check(value, allowed, max_size, what):
    """Общая проверка: расширение из белого списка и размер в пределах."""
    name = getattr(value, 'name', '') or ''
    ext = _extension(name)

    if not ext:
        raise ValidationError('У файла нет расширения — не могу определить тип')

    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(
            f'Файлы «.{ext}» загружать нельзя: браузер выполняет их как код'
        )

    if ext not in allowed:
        raise ValidationError(
            f'Недопустимый формат «.{ext}». Разрешены: '
            + ', '.join(sorted(allowed))
        )

    size = getattr(value, 'size', None)
    if size is not None and size > max_size:
        raise ValidationError(
            f'{what} больше {_human(max_size)} (ваш файл — {_human(size)})'
        )


def validate_image_file(value):
    """Обложка игры, аватар: только картинки до 5 МБ."""
    _check(value, IMAGE_EXTENSIONS, IMAGE_MAX_SIZE, 'Картинка')


def validate_media_file(value):
    """Медиа новости или влога: картинка либо видео до 50 МБ."""
    _check(value, MEDIA_EXTENSIONS, MEDIA_MAX_SIZE, 'Файл')
