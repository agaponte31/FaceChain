"""
URL configuration for FaceRecognition project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from FaceRecognition.views import home, validar, validar_face, registrar, update_query, update_view, disable_query, disable_view, index, register, procesar_frame, manage_users, create_user, modify_user, modify_user_ch, delete_user, error_401, error_403, respuesta, exit

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Ruta para la página principal que muestra el video
    path('register/', register, name='register'),
    path('procesar_frame/', procesar_frame, name='procesar_frame'),
    path('error_401/', error_401, name='error_401'),
    path('error_403/', error_403, name='error_403'),
    path('respuesta/', respuesta, name='respuesta'),
    path('home/', home, name='home'),
    path('validar/', validar, name='validar'),
    path('validar_face/', validar_face, name='validar_face'),
    path('registrar/', registrar, name='registrar'),
    path('update_query/', update_query, name='update_query'),
    path('update_view/', update_view, name='update_view'),
    path('disable_query/', disable_query, name='disable_query'),
    path('disable_view/', disable_view, name='disable_view'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('manage_users/', manage_users, name='manage_users'),
    path('create_user/', create_user, name='create_user'),
    path('modify_user/', modify_user, name='modify_user'),
    path('modify_user_ch/<int:user_id>', modify_user_ch, name='modify_user_ch'),
    path('delete_user/', delete_user, name='delete_user'),
    path('logout/', exit, name='exit'),
]
