# API для работы с коллекцией мемов

## Сервисы

1. **img_api**
- Публичный API для CRUD-операций с базой данной и запросов на API MinIO.
- Swagger UI: http://127.0.0.1:8000/docs
- Методы:
  - GET /memes: получить список всех мемов (пагинация реализована с помощью параметров offset и limit).
  - GET /memes/{meme_id}: получить конкретный мем по его ID.
  - POST /memes: добавить новый мем.
  - PUT /memes/{meme_id}: обновить существующий мем.
  - DELETE /memes/{meme_id}: удалить мем.

2. **minio_api**
- Приватный API для MinIO. Авторизация реализована через Oauth2.
- Swagger UI: http://127.0.0.1:8001/docs
- Методы:
  - POST /create_or_update: загрузить новый файл в хранилище или обновить существующий по имени.
  - GET /get?name={name}: получить информацию (имя, текст, дата модификации) о файле по его имени.
  - GET /list: получить информацию о всех файлах.
  - DELETE /delete?name={name}: удалить файл с определенным именем.

## Запуск проекта

1. Создать сеть: ```docker network create minio-net```

2. Создать контейнеры из директории проекта: ```docker compose up d --build```

3. Перейти в MinIO и создать bucket с именем memebucket: http://127.0.0.1:9001/buckets

4. Создать access key и secret key и добавить в переменные окружения: http://127.0.0.1:9001/access-keys

5. Удалить контейнеры: ```docker compose down```

6. Создать контейнеры: ```docker compose up -d --build```

7. Создать миграции:
```
docker exec -it minio_api poetry run alembic upgrade head
docker exec -it img_api poetry run alembic upgrade head
```

8. (Опционально) прогнать тесты:
```
docker exec -it minio_api poetry run pytest
docker exec -it img_api poetry run pytest
```