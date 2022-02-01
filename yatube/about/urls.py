from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [

    path('author/',
         views.AboutAuthorView.as_view(),
         name='author'
         ),
    # Статичная страница - Информация об авторе

    path('tech/',
         views.AboutTechView.as_view(),
         name='tech'
         ),
    # Статичная страница - Информация о примененных технологиях
]
