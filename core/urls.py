from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path("entrevista/", views.entrevista_view, name="entrevista"), #ESTO ACABO DE AUMENTAR
    path("registro/", views.register_view, name="registro"),

]
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)