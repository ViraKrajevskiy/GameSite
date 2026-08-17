#!/usr/bin/env bash
#
# Переносит админку Django на отдельный поддомен.
# Запускать НА СЕРВЕРЕ, после ./deploy.sh back:
#
#   sudo bash /srv/gamesite/server/setup-admin-subdomain.sh
#
# Скрипт можно запускать повторно — он проверяет, что уже сделано,
# и не ломает то, что настроено.

set -euo pipefail

DOMAIN="${DOMAIN:-virakrajevskiy.duckdns.org}"
ADMIN_DOMAIN="admin.${DOMAIN}"
ADMIN_USER="${ADMIN_USER:-vira}"

SITE_CONF="/etc/nginx/sites-available/gamesite"
ADMIN_CONF="/etc/nginx/sites-available/gamesite-admin"
ADMIN_SRC="/srv/gamesite/server/nginx-gamesite-admin.conf"
HTPASSWD="/etc/nginx/.htpasswd-admin"
ENV_FILE="/srv/gamesite/.env"
STAMP="$(date +%Y%m%d-%H%M%S)"

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()   { printf '    \033[32mok\033[0m %s\n' "$*"; }
skip() { printf '    -- %s\n' "$*"; }
die()  { printf '\n\033[31mОШИБКА:\033[0m %s\n\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Запусти через sudo: sudo bash $0"
[ -f "$SITE_CONF" ]  || die "Не нашёл $SITE_CONF — конфиг сайта называется иначе?"
[ -f "$ADMIN_SRC" ]  || die "Не нашёл $ADMIN_SRC — сначала выкати код: cd /srv/gamesite && ./deploy.sh back"
[ -f "$ENV_FILE" ]   || die "Не нашёл $ENV_FILE"

echo
echo "  Домен сайта:    $DOMAIN"
echo "  Домен админки:  $ADMIN_DOMAIN"
echo "  Пользователь:   $ADMIN_USER (для пароля nginx)"
echo

# Всё, что портится, откатывается из этих копий
BACKUP_DIR="/root/admin-subdomain-backup-$STAMP"
mkdir -p "$BACKUP_DIR"
cp "$SITE_CONF" "$BACKUP_DIR/gamesite.conf"
cp "$ENV_FILE"  "$BACKUP_DIR/env"
ok "копии старых конфигов: $BACKUP_DIR"


# --- 1. Поддомен вообще указывает на нас? -----------------------------------
say "1/7  Проверяю DNS"
SERVER_IP="$(curl -s -4 https://ifconfig.me || echo '')"
RESOLVED="$(getent hosts "$ADMIN_DOMAIN" | awk '{print $1}' | head -1 || echo '')"
if [ -z "$RESOLVED" ]; then
    die "$ADMIN_DOMAIN никуда не резолвится. У DuckDNS поддомены работают сами — проверь, что домен $DOMAIN вообще жив."
fi
if [ -n "$SERVER_IP" ] && [ "$RESOLVED" != "$SERVER_IP" ]; then
    die "$ADMIN_DOMAIN резолвится в $RESOLVED, а сервер — $SERVER_IP. Сертификат не выпустится."
fi
ok "$ADMIN_DOMAIN → $RESOLVED"


# --- 2. Пароль для Basic Auth -----------------------------------------------
say "2/7  Пароль для nginx"
if [ -f "$HTPASSWD" ] && grep -q "^${ADMIN_USER}:" "$HTPASSWD"; then
    skip "пароль для '$ADMIN_USER' уже заведён (сменить: sudo htpasswd $HTPASSWD $ADMIN_USER)"
else
    command -v htpasswd >/dev/null || { apt-get update -qq && apt-get install -y -qq apache2-utils; }
    echo "    Придумай пароль. Это НЕ пароль от Django — отдельный, специально другой."
    echo "    Сохрани его в менеджере паролей: восстановить нельзя, только перезаписать."
    echo
    if [ -f "$HTPASSWD" ]; then
        htpasswd "$HTPASSWD" "$ADMIN_USER"
    else
        htpasswd -c "$HTPASSWD" "$ADMIN_USER"
    fi
    ok "пароль записан"
fi
chown root:www-data "$HTPASSWD"
chmod 640 "$HTPASSWD"


# --- 3. Закрыть /admin/ на публичном домене ---------------------------------
say "3/7  Закрываю /admin/ на $DOMAIN"
python3 - "$SITE_CONF" << 'PYEOF'
import re
import sys

path = sys.argv[1]
with open(path, encoding='utf-8') as fh:
    conf = fh.read()

REPLACEMENT = """location /admin/ {
        # Админка вынесена на отдельный поддомен.
        # 404, а не 403 — чтобы боты не понимали, что путь вообще есть.
        return 404;
    }

    location = /admin {
        return 404;
    }"""


def find_block(text, start):
    """Границы блока location по балансу фигурных скобок."""
    open_brace = text.index('{', start)
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise ValueError('не нашёл закрывающую скобку блока location /admin/')


changed = 0
already = 0
while True:
    match = re.search(r'location\s+/admin/\s*\{', conf)
    if not match:
        break

    start, end = find_block(conf, match.start())
    body = conf[start:end]

    if 'return 404' in body:
        already += 1
        # уже закрыт — помечаем, чтобы не зациклиться, вернём в конце
        conf = conf[:start] + body.replace('location /admin/', 'location /ADMIN_DONE/', 1) + conf[end:]
        continue

    conf = conf[:start] + REPLACEMENT + conf[end:]
    changed += 1

conf = conf.replace('location /ADMIN_DONE/', 'location /admin/')

with open(path, 'w', encoding='utf-8') as fh:
    fh.write(conf)

if changed:
    print(f'    заменено блоков: {changed}')
elif already:
    print(f'    уже закрыто ({already} блок(ов)) — не трогаю')
else:
    print('    блока location /admin/ не нашлось — возможно, уже убран')
PYEOF
ok "публичный домен обработан"


# --- 4. Конфиг поддомена ----------------------------------------------------
say "4/7  Поднимаю $ADMIN_DOMAIN"
if [ -f "$ADMIN_CONF" ] && grep -q "server_name $ADMIN_DOMAIN" "$ADMIN_CONF"; then
    skip "конфиг уже на месте — не перезаписываю (в нём может быть SSL от certbot)"
else
    cp "$ADMIN_SRC" "$ADMIN_CONF"
    sed -i "s/admin\.gamesite\.duckdns\.org/${ADMIN_DOMAIN}/g" "$ADMIN_CONF"
    grep -q "$HTPASSWD" "$ADMIN_CONF" || die "в $ADMIN_CONF ожидался путь $HTPASSWD"
    ok "$ADMIN_CONF записан"
fi
ln -sf "$ADMIN_CONF" /etc/nginx/sites-enabled/gamesite-admin
ok "включён в sites-enabled"

if ! nginx -t 2>/tmp/nginx-test.log; then
    cat /tmp/nginx-test.log >&2
    cp "$BACKUP_DIR/gamesite.conf" "$SITE_CONF"
    rm -f /etc/nginx/sites-enabled/gamesite-admin
    nginx -t >/dev/null 2>&1 && systemctl reload nginx
    die "nginx не принял конфиг — всё откатил, сайт работает как раньше. Лог выше."
fi
systemctl reload nginx
ok "nginx перезагружен"


# --- 5. Сертификат ----------------------------------------------------------
say "5/7  Сертификат Let's Encrypt"
if [ -d "/etc/letsencrypt/live/$ADMIN_DOMAIN" ]; then
    skip "сертификат для $ADMIN_DOMAIN уже есть"
elif certbot certificates 2>/dev/null | grep -q "$ADMIN_DOMAIN"; then
    skip "сертификат уже выпущен"
else
    # Аккаунт ACME уже есть — основной сертификат когда-то выпускался.
    # Если вдруг нет, вторая попытка заводит его без почты.
    certbot --nginx -d "$ADMIN_DOMAIN" --non-interactive --agree-tos --redirect \
        || certbot --nginx -d "$ADMIN_DOMAIN" --non-interactive --agree-tos --redirect \
                   --register-unsafely-without-email \
        || die "certbot не справился. Запусти руками и посмотри, что скажет: sudo certbot --nginx -d $ADMIN_DOMAIN"
    ok "сертификат выпущен, продлевается вместе с основным"
fi


# --- 6. Django ---------------------------------------------------------------
say "6/7  Настраиваю Django"
python3 - "$ENV_FILE" "$DOMAIN" "$ADMIN_DOMAIN" << 'PYEOF'
import sys

env_path, domain, admin_domain = sys.argv[1], sys.argv[2], sys.argv[3]

with open(env_path, encoding='utf-8') as fh:
    lines = fh.read().splitlines()


def upsert(lines, key, value):
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}'
            return lines, 'обновлено'
    lines.append(f'{key}={value}')
    return lines, 'добавлено'


def merge_csv(lines, key, addition, fallback):
    """Дописать значение в список через запятую, не потеряв то, что было."""
    current = fallback
    for line in lines:
        if line.strip().startswith(f'{key}='):
            current = line.split('=', 1)[1].strip()
            break
    items = [x.strip() for x in current.split(',') if x.strip()]
    if addition not in items:
        items.append(addition)
    return upsert(lines, key, ','.join(items))


lines, s1 = merge_csv(lines, 'DJANGO_ALLOWED_HOSTS', admin_domain, domain)
print(f'    DJANGO_ALLOWED_HOSTS — {s1}')

lines, s2 = merge_csv(lines, 'DJANGO_CSRF_TRUSTED_ORIGINS',
                      f'https://{admin_domain}', f'https://{domain}')
print(f'    DJANGO_CSRF_TRUSTED_ORIGINS — {s2}')

lines, s3 = upsert(lines, 'DJANGO_ADMIN_HOST', admin_domain)
print(f'    DJANGO_ADMIN_HOST — {s3}')

with open(env_path, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines) + '\n')
PYEOF
chown ubuntu:ubuntu "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Проверяем настройки ДО рестарта: с битым .env сайт просто не поднимется
if ! sudo -u ubuntu /srv/gamesite/.venv/bin/python /srv/gamesite/manage.py check >/tmp/dj-check.log 2>&1; then
    cat /tmp/dj-check.log >&2
    cp "$BACKUP_DIR/env" "$ENV_FILE"
    chown ubuntu:ubuntu "$ENV_FILE"; chmod 600 "$ENV_FILE"
    die "Django не принял настройки — .env откатил. Лог выше."
fi
ok "настройки валидны"

systemctl restart gamesite
sleep 2
systemctl is-active --quiet gamesite || die "gamesite не поднялся: sudo journalctl -u gamesite -n 50 --no-pager"
ok "gamesite перезапущен"


# --- 7. Проверка ------------------------------------------------------------
say "7/7  Проверяю"
check() {
    local label="$1" url="$2" want="$3"
    local code
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || echo 000)"
    if [ "$code" = "$want" ]; then
        printf '    \033[32mok\033[0m   %-28s %s\n' "$label" "$code"
    else
        printf '    \033[31mПЛОХО\033[0m %-28s %s (ждали %s)\n' "$label" "$code" "$want"
        FAILED=1
    fi
}

FAILED=0
check "сайт открывается"      "https://${DOMAIN}/"                 200
check "/admin/ на сайте нет"  "https://${DOMAIN}/admin/"           404
check "API работает"          "https://${DOMAIN}/api/games/"       200
check "админка просит пароль" "https://${ADMIN_DOMAIN}/admin/"     401
check "на поддомене нет API"  "https://${ADMIN_DOMAIN}/api/games/" 404

echo
if [ "$FAILED" = "0" ]; then
    printf '\033[32m  Готово.\033[0m Админка: https://%s/admin/\n' "$ADMIN_DOMAIN"
    echo "  Сначала спросит логин/пароль браузера ($ADMIN_USER), потом обычная форма Django."
    echo
    echo "  Старые конфиги на всякий случай: $BACKUP_DIR"
else
    printf '\033[31m  Часть проверок не прошла.\033[0m Что смотреть:\n'
    echo "    sudo tail -30 /var/log/nginx/gamesite-admin.error.log"
    echo "    sudo journalctl -u gamesite -n 30 --no-pager"
    echo
    echo "  Откатить всё назад:"
    echo "    sudo cp $BACKUP_DIR/gamesite.conf $SITE_CONF"
    echo "    sudo cp $BACKUP_DIR/env $ENV_FILE"
    echo "    sudo rm -f /etc/nginx/sites-enabled/gamesite-admin"
    echo "    sudo nginx -t && sudo systemctl reload nginx && sudo systemctl restart gamesite"
fi
echo
