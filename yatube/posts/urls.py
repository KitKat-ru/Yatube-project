from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index,
         name='index'
         ),
    # Страница группы
    path('group/<slug:slug>/',
         views.group_posts,
         name='group_list'
         ),
    # Профайл пользователя
    path('profile/<str:username>/',
         views.profile,
         name='profile'
         ),
    # Просмотр записи
    path('posts/<int:post_id>/',
         views.post_detail,
         name='post_detail'
         ),
    # Изменение записи
    path('posts/<int:post_id>/edit/',
         views.post_edit,
         name='update_post'
         ),
    # Создание записи
    path('create/',
         views.post_create,
         name='post_create'
         ),
    # Создание комментария
    path('posts/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'
         ),
    # Виджет подписок
    path('follow/',
         views.follow_index,
         name='follow_index'
         ),
    # Создание подписки на автора
    path('profile/<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'
         ),
    # Прекращение подписки на автора
    path('profile/<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'
         ),
]
