from django.urls import path
from . import views
from .views import ListaObservacionesView, CrearObservacionView 

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
    path("gestionturnos/", views.gestionturnos, name="gestionturnos"),
    path('observaciones/nueva/', CrearObservacionView.as_view(), name='crear_observacion'), 
    path('observaciones/', ListaObservacionesView.as_view(), name='lista_observaciones'),
    path('comprobantes/', views.comprobantes_view, name='comprobantes'),   

     # CRUD Pacientes
    path("pacientes/", views.pacientes_list, name="pacientes_list"),
    path("pacientes/nuevo/", views.paciente_create, name="pacientes_create"),
    path("pacientes/editar/<int:pk>/", views.paciente_update, name="pacientes_update"),
    path("pacientes/eliminar/<int:pk>/", views.paciente_delete, name="pacientes_delete"),

    # TESTIMONIO
    path("testimonios/", views.testimonios_inicio, name="testimonios_inicio"),
    path("testimonios/enviar/", views.enviar_testimonio, name="enviar_testimonio"),

    #  Panel del admin (para profesionales)
    path("dashboard/testimonios/", views.testimonios_lista, name="testimonios_lista"),
    path("dashboard/testimonios/aprobar/<int:id>/", views.aprobar_testimonio, name="aprobar_testimonio"),
    path("dashboard/testimonios/restringir/<int:id>/", views.restringir_testimonio, name="restringir_testimonio"),
    path("testimonios/publicos/", views.testimonios_publicos, name="testimonios_publicos"),
    path("dashboard/testimonios/eliminar/<int:id>/", views.eliminar_testimonio, name="eliminar_testimonio"),
]

