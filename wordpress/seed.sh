#!/bin/bash

echo "[+] Waiting for MySQL..."

until docker compose exec db mysqladmin ping -h "localhost" --silent; do
  sleep 2
done

echo "[+] Inserting users..."

docker compose exec -T db mysql -u wpuser -pwppass wordpress <<EOF

INSERT INTO wp_users (user_login, user_pass, user_email, user_registered)
SELECT 'user', MD5('user123'), 'user@test.local', NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM wp_users WHERE user_login='user'
);

INSERT INTO wp_usermeta (user_id, meta_key, meta_value)
SELECT ID, 'wp_capabilities', 'a:1:{s:10:"subscriber";b:1;}'
FROM wp_users WHERE user_login='user'
ON DUPLICATE KEY UPDATE meta_value=meta_value;

EOF

echo "[+] Waiting for Wordpress container..."

until docker compose exec wordpress wp --info --allow-root >/dev/null 2>&1; do
  sleep 2
done

echo "[+] Installing Simple History plugin..."

docker compose exec wordpress wp plugin install simple-history --activate --allow-root || true

echo "[+] Done"
