from django.urls import path
from . import views

urlpatterns = [
    path("base/", views.base, name="base"),
    path('', views.inicio, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("entrevista/", views.entrevista_view, name="entrevista"), #ESTO ACABO DE AUMENTAR
    path("registro/", views.register_view, name="registro"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("turnos/", views.turnos_view, name="turnos"),
    path("estadistica/", views.estadistica_view, name="estadistica"),
    path("informes/", views.crear_informe, name="informes"),
    path("lista_informes/", views.lista_informes, name="lista_informes"),

     # CRUD Pacientes
    path("pacientes/", views.pacientes_list, name="pacientes_list"),
    path("pacientes/nuevo/", views.paciente_create, name="pacientes_create"),
    path("pacientes/editar/<int:pk>/", views.paciente_update, name="pacientes_update"),
    path("pacientes/eliminar/<int:pk>/", views.paciente_delete, name="pacientes_delete"),

]