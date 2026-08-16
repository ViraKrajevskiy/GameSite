#!/usr/bin/env bash
# Обновление проекта на сервере: бэкенд + фронтенд.
# Использование:  ./deploy.sh          — обновить всё
#                 ./deploy.sh back     — только Django
#                 ./deploy.sh front    — только React
set -euo pipefail

APP_DIR=/srv/gamesite
FRONT_SRC=/srv/gamesite-front-src
FRONT_DIR=/srv/gamesite-front
VENV="$APP_DIR/.venv"

TARGET="${1:-all}"

deploy_back() {
    echo "==> Бэкенд: забираю изменения"
    cd "$APP_DIR"
    git pull --ff-only

    echo "==> Зависимости"
    "$VENV/bin/pip" install -q -r requirements.txt

    echo "==> Миграции"
    "$VENV/bin/python" manage.py migrate --noinput

    echo "==> Статика Django"
    "$VENV/bin/python" manage.py collectstatic --noinput

    echo "==> Проверка конфигурации"
    "$VENV/bin/python" manage.py check --deploy || true

    echo "==> Перезапуск gunicorn"
    sudo systemctl restart gamesite
}

deploy_front() {
    echo "==> Фронтенд: забираю изменения"
    cd "$FRONT_SRC"
    git pull --ff-only

    cd "$FRONT_SRC/my-app"
    echo "==> Сборка"
    npm ci
    npm run build

    echo "==> Публикация"
    sudo rsync -a --delete dist/ "$FRONT_DIR/"
    sudo chown -R www-data:www-data "$FRONT_DIR"
}

case "$TARGET" in
    back)  deploy_back ;;
    front) deploy_front ;;
    all)   deploy_back; deploy_front ;;
    *)     echo "Usage: $0 [all|back|front]"; exit 1 ;;
esac

sudo systemctl reload nginx
echo "==> Готово."
systemctl --no-pager --lines=5 status gamesite
