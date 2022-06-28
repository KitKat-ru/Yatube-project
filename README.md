# Yatube
Сервис для публикации статей и общения с подписчиками.

## Стек технологий:
OC Ubuntu 22.04, Python3.9, Django2.2, Pytest, Sorl-thumbnail, CSS3, Bootstrap, HTML5, Gunicorn, Nginx, PostgreSQL.

## Реализация:
Проект создан на Django по MVT-архитектуре. Размещен на виртуальной машине в Яндекс.Облаке. Сервер запущен через Docker-compose (3 контейнера: django+gunicorn, nginx, psql). Покрыт тестами (использовалась библиотека Pytest).

## Возможности:
1. Реализована регистрация (из коробки), добавлена функция смены(восстановления) пароля через email.
2. Настроена панель администратора (роли: user, admin)
3. Авторизованные пользователи могут вести свой блог, присоединяться к группам и добавлять изображения. Кроме того могут подписываться на других блогеров и комментировать их посты. Неавторизованные пользователи могут только просматривать контент.


[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
