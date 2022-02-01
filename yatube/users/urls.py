from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path('login/', LoginView.as_view(
         template_name='users/login.html'
         ),
         name='login'
         ),
    #  Авторизация
    path('logout/', LogoutView.as_view(
         template_name='users/logged_out.html'
         ),
         name='logout'
         ),
    #  Выход
    path('password_change/',
         PasswordChangeView.as_view(
             template_name='users/password_change_form.html'
         ),
         name='password_change'
         ),
    #  Смена пароля
    path('password_change/done/',
         PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'),
         name='password_change_done'
         ),
    #  Сообщение об успешном изменении пароля
    path('signup/', views.SignUp.as_view(),
         name='signup'
         ),
    #  Регистрация
    path('password_reset/', PasswordResetView.as_view(
         template_name='users/password_reset_form.html'
         ),
         name='password_reset'
         ),
    #  Восстановление пароля, форма
    path('password_reset/done/', PasswordResetDoneView.as_view(
         template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'
         ),
    #  Восстановление пароля, уведомление об отправке письма
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'
         ),
    #  Восстановление пароля, страница подтверждения сброса пароля
    path('reset/done/', PasswordResetCompleteView.as_view(
         template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),
    #  Восстановление пароля, уведомление об успешной смене пароля
]
