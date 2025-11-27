from django.urls import path
from . import views
from .views import ListaObservacionesView, CrearObservacionView 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("base/", views.base, name="base"),
    path('', views.inicio, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("entrevista/", views.entrevista_view, name="entrevista"), #ESTO ACABO DE AUMENTAR
    path("registro/", views.register_view, name="registro"),
    path('dashboard/', views.dashboard, name='dashboard'), #dash especialistas

    path("turnos/", views.turnos_view, name="turnos"),
    path("estadistica/", views.estadistica_view, name="estadistica"),
    path("gestionturnos/", views.gestionturnos, name="gestionturnos"),
    path('observaciones/', ListaObservacionesView.as_view(), name='lista_observaciones'),
    path('observaciones/nueva/', CrearObservacionView.as_view(), name='crear_observacion'),
    path('observaciones/<int:pk>/editar/', views.editar_observacion, name='editar_observacion'),
    path('observaciones/<int:pk>/eliminar/', views.eliminar_observacion, name='eliminar_observacion'),
    path('comprobantes/', views.comprobantes_view, name='comprobantes'),   
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('mi-perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # Informes Interdisciplinarios
    path('informes/', views.lista_informes, name='lista_informes'),
    path('informes/nuevo/', views.crear_informe_interdisciplinario, name='crear_informe_interdisciplinario'),
    path('informes/<int:informe_id>/', views.detalle_informe, name='detalle_informe'),
    path('informes/<int:informe_id>/editar/', views.editar_informe, name='editar_informe'),
    path('informes/<int:informe_id>/eliminar/', views.eliminar_informe, name='eliminar_informe'),
    path('informes/<int:informe_id>/agregar-seccion/', views.agregar_seccion_informe, name='agregar_seccion_informe'),
    path('informes/seccion/<int:seccion_id>/eliminar/', views.eliminar_seccion_informe, name='eliminar_seccion_informe'),
    
     # CRUD Pacientes
    path("pacientes/", views.pacientes_list, name="pacientes_list"),
    path("pacientes/nuevo/", views.paciente_create, name="pacientes_create"),
    path("pacientes/editar/<int:pk>/", views.paciente_update, name="pacientes_update"),
    path("pacientes/eliminar/<int:pk>/", views.paciente_delete, name="pacientes_delete"),
    # Dashboard Pacientes
    path('pacientes/dashboard/', views.dashboard_pacientes, name='dashboard_pacientes'), #dash pacientes
    path('pacientes/turnos/', views.paciente_turnos, name='paciente_turnos'),
    path('pacientes/informes/', views.paciente_informes, name='paciente_informes'),
    path('pacientes/observaciones/', views.paciente_observaciones, name='paciente_observaciones'),
    path('pacientes/comprobantes/', views.paciente_comprobantes, name='paciente_comprobantes'),
    path('pacientes/perfil/', views.paciente_perfil, name='paciente_perfil'),
    
    # TESTIMONIO
    path("testimonios/", views.testimonios_inicio, name="testimonios_inicio"),
    path("testimonios/enviar/", views.enviar_testimonio, name="enviar_testimonio"),

    #  Panel del admin (para profesionales)
    path("dashboard/testimonios/", views.testimonios_lista, name="testimonios_lista"),
    path("dashboard/testimonios/aprobar/<int:id>/", views.aprobar_testimonio, name="aprobar_testimonio"),
    path("dashboard/testimonios/restringir/<int:id>/", views.restringir_testimonio, name="restringir_testimonio"),
    path("dashboard/testimonios/editar/<int:id>/", views.editar_testimonio, name="editar_testimonio"),
    path("testimonios/publicos/", views.testimonios_publicos, name="testimonios_publicos"),
    path("dashboard/testimonios/eliminar/<int:id>/", views.eliminar_testimonio, name="eliminar_testimonio"),
    path("dashboard/estadistica/", views.estadistica_view, name="estadistica"),
    path("dashboard/estadistica/agregar/", views.estadistica_agregar, name="estadistica_agregar"),
    
    # Gestión de Turnos
    path('turnos/gestion/', views.gestion_turnos, name='gestion_turnos'),
    path('turnos/crear/', views.crear_turno, name='crear_turno'),
    path('turnos/editar/<int:pk>/', views.editar_turno, name='editar_turno'),
    path('turnos/confirmar/<int:pk>/', views.confirmar_turno, name='confirmar_turno'),
    path('turnos/cancelar/<int:pk>/', views.cancelar_turno, name='cancelar_turno'),
    path('turnos/eliminar/<int:pk>/', views.eliminar_turno, name='eliminar_turno'),
    
    # Gestión de Entrevistas de Admisión
    path('entrevistas/gestion/', views.gestion_entrevistas, name='gestion_entrevistas'),
    path('entrevistas/ver/<int:pk>/', views.ver_entrevista, name='ver_entrevista'),
    path('entrevistas/derivar/<int:pk>/', views.derivar_entrevista, name='derivar_entrevista'),
    
    # Gestión de Contactos
    path('contactos/', views.lista_contactos, name='lista_contactos'),
    path('contactos/<int:pk>/leido/', views.marcar_contacto_leido, name='marcar_contacto_leido'),
    path('contactos/<int:pk>/respondido/', views.marcar_contacto_respondido, name='marcar_contacto_respondido'),
    
]    
    
    