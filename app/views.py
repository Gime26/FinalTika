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


def crear_informe(request):
    if request.method == 'POST':
        form = InformeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_informes')
    else:
        form = InformeForm()
    return render(request, 'informes.html', {'form': form})

def lista_informes(request):
    informes = Informe.objects.all()
    return render(request, 'lista_informes.html', {'informes': informes})
# --- Vista para Listar (Historial) ---

class ListaObservacionesView(LoginRequiredMixin, ListView):
    model = Observacion
    template_name = 'observaciones/observacion_list.html'
    context_object_name = 'observaciones'
    ordering = ['-fecha']
    
class CrearObservacionView(LoginRequiredMixin, CreateView):
    model = Observacion
    form_class = ObservacionForm
    template_name = 'observaciones/observacion_form.html'
    success_url = reverse_lazy('lista_observaciones')

    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        return super().form_valid(form)

def comprobantes_view(request):
    return render(request, 'comprobantes.html')

def enviar_testimonio(request):
    if request.method == 'POST':
        form = TestimonioForm(request.POST)
        if form.is_valid():
            testimonio = form.save(commit=False)
            testimonio.usuario = request.user if request.user.is_authenticated else None
            testimonio.save()
            return redirect('index')
    else:
        form = TestimonioForm()
    return render(request, 'testimonio/enviar_testimonio.html', {'form': form})

# Mostrar testimonios públicos (aprobados)
def testimonios_publicos(request):
    testimonios = Testimonio.objects.filter(estado='aprobado', publicado=True).order_by('-fecha_envio')
    return render(request, 'testimonios_publicos.html', {'testimonios': testimonios})



def testimonios_lista(request):
    testimonios = Testimonio.objects.all().order_by('-fecha_envio')
    return render(request, 'dashboard/testimonios.html', {'testimonios': testimonios})
# Acciones del admin 
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
def testimonios_inicio(request):
    testimonios = Testimonio.objects.filter(publicado=True).order_by('-fecha_envio')
    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})

def eliminar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.delete()
    return redirect('testimonios_lista')
