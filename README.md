# Блогикум. Часть 3

Учебный проект на Django. Пользователи могут регистрироваться, публиковать
записи с изображениями и оставлять комментарии. Лента, категории и профили
поддерживают постраничный вывод. Автор управляет своими записями и комментариями.

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python blogicum/manage.py migrate
python blogicum/manage.py runserver
```

Категории и локации создаются в административной панели. Для доступа к ней
создайте администратора командой `python blogicum/manage.py createsuperuser`.
Демонстрационные записи можно загрузить командой
`python blogicum/manage.py loaddata db.json` из корня репозитория.

Письма сохраняются локально в `blogicum/sent_emails/`. Проверки запускаются
из корня репозитория командой `python -m pytest`.
