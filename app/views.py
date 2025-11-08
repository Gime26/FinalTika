from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm, InformeForm, ObservacionForm, TestimonioForm
from .models import Entrevista, EstadoPaciente, Informe, Perfil, Paciente, Observacion, Testimonio
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

def base(request):
    return render(request, "base.html")

def inicio(request):
    # Instanciar ambos formularios para los modales en index.html
    login_form = LoginForm()
    entrevista_form = EntrevistaForm() 
    
    # Usamos nombres específicos en el contexto para evitar conflictos
    context = {
        'login_form': login_form, 
        'entrevista_form': entrevista_form,
    }
    
    return render(request, 'index.html', context)


# Vista para mostrar el modal/login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            # 1. Los datos se obtienen SOLO si el formulario es válido
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # 2. Intenta autenticar
            user = authenticate(request, username=username, password=password)
            
            # 3. La comprobación del usuario se hace DENTRO de form.is_valid()
            if user is not None:
                login(request, user)
                # Si Django pasa un parámetro 'next', redirige ahí
                next_url = request.POST.get('next') or 'dashboard' 
                return redirect(next_url) 
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        
        # Si el formulario no es válido, o si la autenticación falla,
        # el código continúa ejecutándose hasta el return final.
        
    else:
        form = LoginForm()

    # Si se accede directamente a /login/ o si el POST falla, 
    # se renderiza la plantilla de login dedicada con el formulario y mensajes.
    return render(request, 'login.html', {'form': form})


# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')  # redirige al inicio


# Vista para procesar la Entrevista desde el modal en index.html
def entrevista_view(request):
    if request.method == 'POST':
        form = EntrevistaForm(request.POST)
        if form.is_valid():
            # Guarda la entrevista en la base de datos (asumiendo que EntrevistaForm es un ModelForm)
            form.save()
            messages.success(request, "Entrevista enviada correctamente. Pronto nos pondremos en contacto.")
            return redirect('inicio') # Redirige a inicio después del éxito (cambia 'gracias' por la URL que uses)
        else:
            # Si la validación falla, volvemos a renderizar index.html con los errores
            # También debemos pasar el LoginForm para que el otro modal no se rompa
            login_form = LoginForm() 
            context = {
                'entrevista_form': form, # El formulario con errores
                'login_form': login_form,
            }
            messages.error(request, "Error en el formulario de entrevista. Por favor, revisa los campos.")
            return render(request, 'index.html', context) 
    else:
        # Si se accede por GET, redirige al inicio
        return redirect('inicio')


# Vista de registro
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 1. Guarda el objeto User
            user = form.save()
            
            # 2. Crea el objeto Perfil y asocia el User
            Perfil.objects.create(
                user=user,
                numero_documento=form.cleaned_data.get('numero_documento'),
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                domicilio=form.cleaned_data.get('domicilio'),
                telefono=form.cleaned_data.get('telefono'),
            )
            
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect('login') 
        else:
             # Si el registro falla
            messages.error(request, "Error en el formulario de registro. Por favor, verifica los datos.")
    else:
        form = RegisterForm()
        
    return render(request, 'register.html', {'form': form}) 

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def turnos_view(request):
    return render(request, 'turnos.html')

def gestionturnos(request):
    return render(request, 'gestionturnos.html')


def pacientes_list(request):
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes/pacientes_list.html', {'pacientes': pacientes})

def paciente_create(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/pacientes_form.html', {'form': form})


def paciente_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/pacientes_form.html', {'form': form})

def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('pacientes_list') 
    
    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})

def estadistica_view(request):
    estados = EstadoPaciente.objects.all()
    return render(request, 'estadistica.html', {'estados': estados})   

def formulario_informe(request):
    """Muestra el template del formulario de informes."""
    # El template que te di se llama informes_formulario.html
    return render(request, 'informes_formulario.html') 

# 2. Vista para manejar el POST y guardar los datos
def guardar_informe(request):
    """Procesa los datos del formulario y los guarda en la base de datos."""
    
    # Asegúrate de que el método de la solicitud sea POST
    if request.method == 'POST':
        # Recupera los datos del formulario usando los atributos 'name' del HTML
        asunto_data = request.POST.get('asunto')
        fecha_data = request.POST.get('fecha')
        hora_data = request.POST.get('hora')
        contenido_data = request.POST.get('contenido')
        
        # Crea y guarda una nueva instancia del modelo Informe
        nuevo_informe = Informe.objects.create(
            asunto=asunto_data,
            fecha=fecha_data,
            hora=hora_data,
            contenido=contenido_data
        )
        
        # Opcional: Redirige al usuario a una página de éxito o al dashboard
        # Por ejemplo, podrías usar 'dashboard' o 'informes_listado'
        return redirect('dashboard') 
        
    # Si la solicitud no es POST (por ejemplo, alguien intenta acceder directamente),
    # simplemente redirige al formulario o al dashboard.
    return redirect('formulario_informe')


class ListaObservacionesView(LoginRequiredMixin, ListView):
    """Muestra el historial de todas las observaciones."""
    model = Observacion
    template_name = 'observaciones/registro_observaciones.html' # Mismo HTML
    context_object_name = 'historial_observaciones'
    ordering = ['-fecha'] # Ordenar por fecha más reciente

    def get_context_data(self, **kwargs):
        # Esto permite que la plantilla reciba ambos datos: el formulario vacío y el historial
        context = super().get_context_data(**kwargs)
        context['form'] = ObservacionForm()
        return context
    

class CrearObservacionView(LoginRequiredMixin, CreateView):
    """Maneja la creación de una nueva observación."""
    model = Observacion
    form_class = ObservacionForm
    template_name = 'observaciones/registro_observaciones.html' # <--- Usar el HTML de historial
    success_url = reverse_lazy('lista_observaciones') # <--- Apunta a la URL de listado


def comprobantes_view(request):
    return render(request, 'comprobantes.html')

def enviar_testimonio(request):
    if request.method == 'POST':
        form = TestimonioForm(request.POST, request.FILES)
        if form.is_valid():
            testimonio = form.save(commit=False)
            testimonio.usuario = request.user if request.user.is_authenticated else None
            testimonio.save()
            return redirect('index')
    else:
        form = TestimonioForm()
    return render(request, 'testimonio/enviar_testimonio.html', {'form': form})


#  Mostrar testimonios públicos (solo los aprobados y publicados)
def testimonios_publicos(request):
    testimonios = Testimonio.objects.filter(
        estado='aprobado', publicado=True
    ).order_by('-fecha_envio')
    return render(request, 'testimonios_publicos.html', {'testimonios': testimonios})


# ✅ Vista del panel (administración interna)
def testimonios_lista(request):
    testimonios = Testimonio.objects.all().order_by('-fecha_envio')
    return render(request, 'dashboard/testimonios.html', {'testimonios': testimonios})


# ✅ Acciones del panel de administración
def aprobar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'aprobado'
    testimonio.publicado = True
    testimonio.save()
    return redirect('testimonios_lista')


def restringir_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'restringido'
    testimonio.publicado = False
    testimonio.save()
    return redirect('testimonios_lista')


def eliminar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.delete()
    return redirect('testimonios_lista')


# ✅ Página de inicio que muestra los testimonios públicos
def testimonios_inicio(request):
    testimonios = Testimonio.objects.filter(
        publicado=True, estado='aprobado'
    ).order_by('-fecha_envio')
    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})