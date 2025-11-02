from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path("entrevista/", views.entrevista_view, name="entrevista"), #ESTO ACABO DE AUMENTAR
    path("registro/", views.register_view, name="registro"),

]
