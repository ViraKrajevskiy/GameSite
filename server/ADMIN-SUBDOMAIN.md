# Админка на отдельном поддомене

Было: `https://virakrajevskiy.duckdns.org/admin/` — форма входа висит на публичном
домене, её находит любой сканер.

Стало: `https://admin.virakrajevskiy.duckdns.org/admin/` — отдельный хост, закрытый
HTTP Basic Auth. На публичном домене `/admin/` отдаёт 404.

Три слоя: Basic Auth в nginx → форма входа Django → проверка хоста в самом
Django (`AdminHostMiddleware`). Последний слой нужен на случай, если конфиг
nginx когда-нибудь затрут — тогда админка всё равно не всплывёт на главном
домене.

**DNS настраивать не надо.** DuckDNS отдаёт все поддомены на тот же адрес:
`admin.virakrajevskiy.duckdns.org` уже резолвится в 167.172.191.171.

---

## Установка

Всё выполняется на сервере: `ssh -p 2222 ubuntu@167.172.191.171`

### 1. Забрать новый код

```bash
cd /srv/gamesite && ./deploy.sh back
```

### 2. Завести пароль для Basic Auth

```bash
sudo apt install -y apache2-utils          # если htpasswd ещё нет
sudo htpasswd -c /etc/nginx/.htpasswd-admin vira
sudo chown root:www-data /etc/nginx/.htpasswd-admin
sudo chmod 640 /etc/nginx/.htpasswd-admin
```

Пароль спросит интерактивно. Это **не** пароль от Django — отдельный,
специально другой. Сохрани в менеджере паролей, восстановить его нельзя,
только перезаписать той же командой без `-c`.

### 3. Закрыть /admin/ на основном домене

Живой конфиг правится **руками**, копировать поверх файл из репозитория нельзя:
в живой уже вписан SSL-блок от certbot, и копия его затрёт.

```bash
sudo nano /etc/nginx/sites-available/gamesite
```

Найти блок (он встретится в 443-й секции):

```nginx
location /admin/ {
    proxy_pass http://gamesite_app;
    ...
}
```

и заменить целиком на:

```nginx
location /admin/ {
    return 404;
}
location = /admin {
    return 404;
}
```

Образец целиком лежит в `server/nginx-gamesite.conf`.

### 4. Поднять поддомен

```bash
sudo cp /srv/gamesite/server/nginx-gamesite-admin.conf \
        /etc/nginx/sites-available/gamesite-admin
sudo sed -i 's/admin\.gamesite\.duckdns\.org/admin.virakrajevskiy.duckdns.org/' \
        /etc/nginx/sites-available/gamesite-admin
sudo ln -s /etc/nginx/sites-available/gamesite-admin /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

`nginx -t` обязателен. Если ругается на `duplicate upstream` — значит
`upstream gamesite_app` продублировался; в админском конфиге его быть не должно.

### 5. Сертификат на поддомен

```bash
sudo certbot --nginx -d admin.virakrajevskiy.duckdns.org
```

Certbot сам допишет 443-й блок и редирект с 80-го. Продлевается вместе с
основным, отдельный крон не нужен.

### 6. Сказать Django про новый хост

```bash
sudo nano /srv/gamesite/.env
```

```ini
DJANGO_ALLOWED_HOSTS=virakrajevskiy.duckdns.org,admin.virakrajevskiy.duckdns.org
DJANGO_CSRF_TRUSTED_ORIGINS=https://virakrajevskiy.duckdns.org,https://admin.virakrajevskiy.duckdns.org
DJANGO_ADMIN_HOST=admin.virakrajevskiy.duckdns.org
```

`DJANGO_ADMIN_HOST` — тот самый третий слой. Без него middleware ничего не
проверяет, и вся защита держится только на nginx.

```bash
sudo systemctl restart gamesite
```

---

## Проверка

```bash
# на публичном домене админки нет
curl -s -o /dev/null -w "main /admin/  → %{http_code}\n" \
     https://virakrajevskiy.duckdns.org/admin/

# поддомен просит пароль
curl -s -o /dev/null -w "admin без пароля → %{http_code}\n" \
     https://admin.virakrajevskiy.duckdns.org/admin/

# с паролем пускает
curl -s -o /dev/null -u vira -w "admin с паролем → %{http_code}\n" \
     https://admin.virakrajevskiy.duckdns.org/admin/

# на поддомене больше ничего нет
curl -s -o /dev/null -w "admin /api/ → %{http_code}\n" \
     https://admin.virakrajevskiy.duckdns.org/api/games/
```

Ожидаемое:

| Запрос | Код |
|---|---|
| `main /admin/` | **404** |
| `admin` без пароля | **401** |
| `admin` с паролем | **302** (редирект на форму входа Django) |
| `admin /api/` | **404** |

В браузере открой `https://admin.virakrajevskiy.duckdns.org/admin/`: сначала
окно браузера с логином/паролем, потом обычная форма Django. Стили должны
подгрузиться — если админка голая, значит не отдаётся `/static/`, проверь
`ls /srv/gamesite/staticfiles/admin/`.

Сайт при этом должен работать как раньше: `curl -sI https://virakrajevskiy.duckdns.org/`.

---

## Если что-то пошло не так

**Забыл пароль от Basic Auth** — перезаписать:
`sudo htpasswd /etc/nginx/.htpasswd-admin vira` (без `-c`, иначе затрёт файл целиком).

**Заблокировал сам себя `allow/deny`** — правило снимается только с сервера:
`sudo nano /etc/nginx/sites-available/gamesite-admin`, закомментировать строки,
`sudo systemctl reload nginx`.

**404 на самом поддомене после входа** — проверь `DJANGO_ADMIN_HOST` в `.env`:
если там опечатка, middleware не узнаёт свой хост и режет всё подряд.
`sudo journalctl -u gamesite -n 30 --no-pager`.

**Откатить всё назад:**

```bash
sudo rm /etc/nginx/sites-enabled/gamesite-admin
# в /etc/nginx/sites-available/gamesite вернуть proxy_pass вместо return 404
# в /srv/gamesite/.env убрать строку DJANGO_ADMIN_HOST
sudo nginx -t && sudo systemctl reload nginx && sudo systemctl restart gamesite
```
