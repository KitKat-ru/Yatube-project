<h1 align="center">Привет, меня зовут <a href="https://t.me/Taeray" target="_blank">Артем</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>
<h3 align="center">Начинающий Python Developer</h3>
<h3 align="center">Yatube - Сервис для публикации статей и общения с подписчиками.</h3>


## Стек технологий:
OC Ubuntu 22.04, Python3.9, Django2.2, Unittest, Sorl-thumbnail, CSS3, Bootstrap, HTML5, Gunicorn, Nginx, PostgreSQL.

## Реализация:
Проект создан на Django по MVT-архитектуре. Размещен на виртуальной машине в Яндекс.Облаке. Сервер запущен через Docker-compose (3 контейнера: django+gunicorn, nginx, psql). Покрыт тестами (использовалась библиотека Unittest).

## Возможности:
1. Реализована регистрация (из коробки), добавлена функция смены пароля через email. Восстановление пароля есть, но работает в тестовом режиме (письма приходят на сервер разработчика).
2. Настроена панель администратора (роли: user, admin).
3. Авторизованные пользователи могут вести свой блог, присоединяться к группам и добавлять изображения. Кроме того могут подписываться на других блогеров и комментировать их посты. Неавторизованные пользователи могут только просматривать контент.

## Установка:

### На хост-сервере клонируйте репозиторий:

    git clone git@github.com:KitKat-ru/Yatube-project.git

### Перейдите в папку `infra` для этого введите в командной строке:
    cd Yatube-project/infra

### Пример файла `.env`. Должен находится в папке `./Yatube-project/infra/`: ###

    SECRET_KEY=... (ключ к Джанго проекту)
    DB_ENGINE=django.db.backends.postgresql (указываем, что работаем с postgresql)
    DB_NAME=postgres (имя базы данных)
    POSTGRES_USER=... (логин для подключения к базе данных)
    POSTGRES_PASSWORD=... (пароль для подключения к БД (установите свой)
    DB_HOST=db (название сервиса (контейнера)
    DB_PORT=5432 (порт для подключения к БД)

### Подготовьте ВМ. Остановите службу nginx. Установите - [Docker и Docker-compose](https://docs.docker.com/engine/install/ubuntu/): ###

    sudo apt update && sudo apt upgrade -y
    sudo systemctl stop nginx
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo apt install docker-ce docker-compose -y

### Запустите файл `docker-compose.yml` командой:
    sudo docker-compose up -d --build

### Сайт находится по адресу - [Yatube](http://84.201.160.195/)

### Для проверки панели администратора введите

    sudo docker-compose exec web python manage.py createsuperuser

# Авторы:
- Фабриков Артем (GitHub: https://github.com/KitKat-ru/)

# Лицензия
Этот проект лицензируется в соответствии с лицензией MIT

![](https://miro.medium.com/max/156/1*A0rVKDO9tEFamc-Gqt7oEA.png "1")
