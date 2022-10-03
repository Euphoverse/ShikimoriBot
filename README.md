<h1 align="center">Shikimori Bot</h1>

<p align="center">
<a href="https://www.codefactor.io/repository/github/justlian/shikimoribot"><img src="https://www.codefactor.io/repository/github/justlian/shikimoribot/badge" alt="CodeFactor" /></a> <a href="https://discord.gg/AjqX5PB3Uj"><img src="https://discord.com/api/guilds/981818711608524830/widget.png" alt="Discord invite"></a>
</p>

Бот с узконаправленным функционалом, разработанный спецаильно для сервера [Euphoverse Discord](https://discord.justlian.com) и партнёрских серверов Euphoverse Team

## Запуск бота

**Создание копии репозитория**

```
git clone https://github.com/JustLian/ShikimoriBot
cd ShikimoriBot
```

**Установка необходимых библиотек**

```
python -m pip install -r requirements.txt
```

**Создание .env файла**

```
prod-token:"Токен основного бота"
test-token:"Токен тестового бота"

qiwi_auth_key:"Секретный ключ QIWI P2P"

mongo_host="IP MongoDB"
mongo_usename="Имя пользователя MongoDB"
mongo_password="Пароль пользователя MongoDB"
```

**Запуск бота**

```
python -m shiki
```

## Помощь с разработкой

Создайте форк этого репозитория, загружайте туда свои изменения и создавайте PR.
