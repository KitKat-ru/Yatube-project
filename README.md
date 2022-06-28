# Yatube
Сервис для публикации статей и общения с подписчиками.

## Стек технологий:
OC Ubuntu 22.04, Python3.9, Django2.2, Unittest, Sorl-thumbnail, CSS3, Bootstrap, HTML5, Gunicorn, Nginx, PostgreSQL.

## Реализация:
Проект создан на Django по MVT-архитектуре. Размещен на виртуальной машине в Яндекс.Облаке. Сервер запущен через Docker-compose (3 контейнера: django+gunicorn, nginx, psql). Покрыт тестами (использовалась библиотека Unittest).

## Возможности:
1. Реализована регистрация (из коробки), добавлена функция смены пароля через email. Восстановление пароля есть, но работает в тестовом режиме (письма приходят на сервер разработчика).
2. Настроена панель администратора (роли: user, admin).
3. Авторизованные пользователи могут вести свой блог, присоединяться к группам и добавлять изображения. Кроме того могут подписываться на других блогеров и комментировать их посты. Неавторизованные пользователи могут только просматривать контент.

## Установка:

### Клонируйте репозиторий:

    git clone git@github.com:KitKat-ru/Yatube-project.git

### Перейдите в репозиторий в командной строке:
    cd Yatube-project
  
### Создайте и активируйте виртуальное окружение:
    python3.9 -m venv env
#### для Mac OS/Linux:
    source env/bin/activate
#### для Windows OS:
    source venv/Scripts/activate
  
### Установите зависимости из файла requirements.txt:
#### Обновите пакеты:
    python3 -m pip install --upgrade pip
#### Установите зависимости: 
    pip install -r requirements.txt

## При необходимости
### Создайте миграции:
    python3 manage.py makemigrations
### Примените миграции:
    python3 manage.py migrate
  
### Запустите проект:
    python3 manage.py runserverо:

Сайт находится по адресу - [Yatube](http://taeray.sytes.net/).
