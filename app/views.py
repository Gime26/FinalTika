from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm,TurnoForm, ObservacionForm, TestimonioForm, PerfilUpdateForm, InformeInterdisciplinarioForm
from .models import Entrevista, EstadoPaciente, Perfil, Paciente, Observacion, Testimonio, Turno, STATUS_CHOICES, Especialista
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib.auth import get_user_model 
from .decorators import solo_terapeutas, solo_pacientes
from django.conf import settings
from django.views.decorators.http import require_POST


@login_required
def mi_perfil(request):
    perfil = request.user.perfil
    
    # 💡 MEJORA: Advertencia más dinámica. 
    # Si el rol es especialista, debe tener la matricula
    advertencia = False
    if perfil.rol == 'especialista' and not perfil.matricula:
        advertencia = True 

    if request.method == 'POST':
        form = PerfilUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            
            # Si el usuario es un especialista y actualizó su perfil, podrías querer 
            # sincronizar o crear el objeto Especialista principal aquí si no existe.
            if perfil.rol == 'especialista' and not perfil.especialista_rel:
                # Lógica para asociar o crear el objeto Especialista único:
                especialista_obj, created = Especialista.objects.get_or_create(
                    dni=perfil.dni,
                    defaults={
                        'nombre': perfil.nombre + " " + perfil.apellido,
                        'especialidad': perfil.especialidad,
                        'matricula': perfil.matricula,
                        'email': perfil.email,
                        'telefono': perfil.telefono,
                    }
                )
                perfil.especialista_rel = especialista_obj
                perfil.save()
                messages.info(request, "Perfil de Especialista sincronizado con la base de datos principal.")

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('mi_perfil')
    else:
        form = PerfilUpdateForm(instance=perfil)

    return render(request, 'mi_perfil.html', {
        'form': form,
        'advertencia': advertencia,
        'perfil': perfil
    })

def base(request):
    return render(request, "base.html")  # o el template que corresponda

def inicio(request):
    return render(request, "index.html")  # O el template que uses de inicio

@solo_terapeutas
def dashboard_terapeutas(request):
    # Si el usuario es terapeuta/especialista, mostramos los turnos que le corresponden
    try:
        especialista_rel = request.user.perfil.especialista_rel
        if especialista_rel:
            turnos_proximos = Turno.objects.filter(
                especialista=especialista_rel
            ).exclude(
                status__in=['CANCELLED', 'COMPLETED']
            ).order_by('date', 'time')
            
            context = {
                'especialista': especialista_rel,
                'turnos_proximos': turnos_proximos
            }
        else:
            messages.warning(request, "Tu perfil de especialista no está completamente asociado. Contacta a un administrador.")
            context = {'turnos_proximos': []}

    except Perfil.DoesNotExist:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('login') 
        
    return render(request, 'dashboard.html', context)


# DASHBOARD PACIENTES

@login_required
def dashboard_pacientes(request):
    
    try:
        perfil_del_usuario = request.user.perfil
        
        # 🛑 CORRECCIÓN: Evitar que los especialistas ejecuten esta lógica
        if perfil_del_usuario.rol != 'paciente':
            messages.warning(request, "Acceso denegado. Solo pacientes pueden ver este dashboard.")
            return redirect('dashboard') # Redirigir al dashboard correcto
            
        # ... El resto del código solo se ejecuta si el rol es 'paciente' ...
        
        # Paso 2: OBTENER EL PACIENTE ASOCIADO A ESE PERFIL (¡Esto sigue siendo correcto para PACIENTES!)
        paciente_perfil = perfil_del_usuario.paciente 
        
        # ... (Validación de paciente_perfil is None, que ya tienes) ...
        if paciente_perfil is None:
            messages.error(request, "Error: Tu perfil de paciente no está completamente asociado. Contacta a un administrador.")
            return redirect('login') 
            
        # Paso 3: FILTRAR LOS TURNOS 
        turnos = Turno.objects.filter(paciente=paciente_perfil).order_by('date')

    except AttributeError:
        # El usuario no tiene un objeto 'perfil' asociado.
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('login') 
        
    except Exception as e:
        # Si hay un error en el filtro de Turnos 
        messages.error(request, f"Error al filtrar turnos. Revisa el modelo Turno y su campo de relación. Mensaje: {e}")
        return redirect('login')


    context = {
        'turnos': turnos,
        'paciente': paciente_perfil,
        'perfil': perfil_del_usuario,
    }
    return render(request, 'pacientes/dashboard_pacientes.html', context)


@login_required
def paciente_turnos(request):
    return render(request, "pacientes/paciente_turnos.html")

@login_required
def paciente_informes(request):
    return render(request, "pacientes/paciente_informes.html")

@login_required
def paciente_observaciones(request):
    return render(request, "pacientes/paciente_observaciones.html")

@login_required
def paciente_comprobantes(request):
    return render(request, "pacientes/paciente_comprobantes.html")

@login_required
def paciente_perfil(request):
    return render(request, "pacientes/paciente_perfil.html")

# Vista para mostrar el modal/login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # 🚨 VALIDACIÓN Y REDIRECCIÓN
                try:
                    perfil = user.perfil
                # CAMBIA la captura de la excepción a la que siempre está disponible:
                except Perfil.DoesNotExist:
                    messages.error(request, "Tu cuenta no tiene un perfil asociado. Contacta al administrador.")
                    return redirect("login")

                # 🛑 CORRECCIÓN 1: Usar 'especialista' en lugar de 'terapeuta'
                if perfil.rol == "especialista":
                    return redirect("dashboard") # Dashboard del Especialista

                # 🛑 CORRECCIÓN 2: Usar 'elif' para ser explícito
                elif perfil.rol == "paciente": 
                    return redirect("dashboard_pacientes")
                
                else:
                    messages.error(request, "Rol de usuario desconocido.")
                    return redirect("login")

            else:
                form.add_error(None, "Usuario o contraseña incorrectos")

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})
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
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            fecha_nacimiento_data = form.cleaned_data["fecha_nacimiento"]

            perfil = Perfil.objects.create(
                user=user,
                nombre=form.cleaned_data["first_name"],
                apellido=form.cleaned_data["last_name"],
                dni=form.cleaned_data["dni"],
                telefono=form.cleaned_data["telefono"],
                email=form.cleaned_data["email"],
                rol="paciente"
            )

            # ✅ CORRECCIÓN CLAVE: El campo en el modelo unificado Paciente es 'dni', no 'dni_paciente'.
            paciente_obj = Paciente.objects.create(
                dni=perfil.dni, # Corregido de dni_paciente
                nombre=perfil.nombre,
                apellido=perfil.apellido,
                fecha_nacimiento=fecha_nacimiento_data,
                telefono=perfil.telefono,
                email=perfil.email,
                genero='O' # Asegurando que sea 'O' (Otro) como en el modelo
            )
            
            # 💡 MEJORA: Asociar el paciente recién creado al perfil
            perfil.paciente = paciente_obj
            perfil.save()
            
            messages.success(request, "Cuenta creada exitosamente. Por favor, inicia sesión.")

            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "registro.html", {"form": form})

@login_required
def dashboard(request): 
    # Decide a dónde ir según el rol
    if request.user.perfil.rol == 'especialista':
        return dashboard_terapeutas(request)
    elif request.user.perfil.rol == 'paciente':
        return dashboard_pacientes(request)
    return redirect('inicio') # Fallback

def turnos_view(request):
    return render(request, 'turnos.html')



def pacientes_list(request):
    pacientes = Paciente.objects.all()
    return render(request, "pacientes/pacientes_list.html", {"pacientes": pacientes})


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

# La vista de guardar informe interdisciplinario (sin cuerpo) fue eliminada/reemplazada por la de abajo.


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
        form = TestimonioForm(request.POST, request.FILES)
        if form.is_valid():
            testimonio = form.save(commit=False)
            testimonio.usuario = request.user if request.user.is_authenticated else None
            testimonio.save()
            messages.success(request, "Testimonio enviado para revisión.")
            return redirect('inicio')
        else:
            messages.error(request, "Hubo un error al enviar el testimonio. Revise los campos.")
    else:
        form = TestimonioForm()
    return render(request, 'testimonio/enviar_testimonio.html', {'form': form})


#  Mostrar testimonios públicos (solo los aprobados y publicados)
def testimonios_publicos(request):
    testimonios = Testimonio.objects.filter(
        estado='aprobado', publicado=True
    ).order_by('-fecha_envio')
    return render(request, 'testimonios_publicos.html', {'testimonios': testimonios})



def testimonios_lista(request):
    testimonios = Testimonio.objects.all().order_by('-fecha_envio')
    return render(request, 'dashboard/testimonios.html', {'testimonios': testimonios})


# ✅ Acciones del panel de administración
def aprobar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'aprobado'
    testimonio.publicado = True
    testimonio.save()
    messages.success(request, f"Testimonio N°{id} aprobado y publicado.")
    return redirect('testimonios_lista')


def restringir_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'restringido'
    testimonio.publicado = False
    testimonio.save()
    messages.warning(request, f"Testimonio N°{id} restringido y retirado de la publicación.")
    return redirect('testimonios_lista')


def eliminar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.delete()
    messages.success(request, f"Testimonio N°{id} eliminado permanentemente.")
    return redirect('testimonios_lista')


# ✅ Página de inicio que muestra los testimonios públicos
def testimonios_inicio(request):
    testimonios = Testimonio.objects.filter(
        publicado=True, estado='aprobado'
    ).order_by('-fecha_envio')
    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})


def crear_informe_interdisciplinario(request):
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Informe Interdisciplinario creado exitosamente.")
            return redirect('dashboard') # Redirige al dashboard
    else:
        form = InformeInterdisciplinarioForm()
    return render(request, 'salud/crear_informe_interdisciplinario.html', {'form': form})


# --- Vistas de Lógica de Turnos ---

# Vista principal que combina el formulario y la lista
class Gestionturnos(LoginRequiredMixin, ListView):
    """Maneja la vista principal de gestión de turnos (Formulario + Lista)."""
    model = Turno
    template_name = 'Turnos/Gestionturnos.html'
    context_object_name = 'turnos' # Cambio a minúscula por convención
    
    # Filtra los turnos que no estén cancelados u ordenados
    queryset = Turno.objects.exclude(status='CANCELLED').order_by('date', 'time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Manejo del Formulario (para crear un nuevo turno)
        context['form'] = TurnoForm()
        
        # 2. Preparar el estado para el template (para mostrar opciones de acción)
        context['status_options'] = STATUS_CHOICES

        # La lógica de mock data se elimina en el código productivo.
        # Asumiendo que los datos están cargados o que el administrador los cargará.

        return context

    def post(self, request, *args, **kwargs):
        """Maneja la solicitud POST para crear un nuevo turno."""
        form = TurnoForm(request.POST)
        if form.is_valid():
            try:
                turno = form.save(commit=False)
                # La validación de slot se realiza en el clean() del formulario/modelo
                turno.full_clean() 
                turno.save()
                messages.success(request, "Turno asignado exitosamente.")
            except Exception as e:
                # Captura la excepción de validación si full_clean falla
                messages.error(request, f"Error al guardar el turno: {e}")
            
            return redirect('turnos:Gestionturnos')
        
        # Si el formulario no es válido, renderizar con errores
        context = self.get_context_data()
        context['form'] = form # Pasar el formulario con errores
        messages.error(request, "Error de validación al asignar el turno. Revise los campos.")
        return self.render_to_response(context)

# Vista para modificar un turno existente
def edit_turno(request, pk):
    """Permite cargar el formulario con datos de un turno existente para modificarlo."""
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Turno N°{pk} modificado exitosamente.")
                return redirect('turnos:Gestionturnos')
            except Exception as e:
                messages.error(request, f"Error al modificar el turno: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            messages.error(request, "Error de validación al modificar el turno. Revise los campos.")

    # Redirige para evitar que la vista quede colgada, asumiendo que el GET se maneja en TurnoView
    return redirect('gestion_turnos')



@require_POST
def confirm_turno(request, pk):
    """Confirma un turno, cambiando su estado a CONFIRMED."""
    # ✅ CORRECCIÓN: el objeto era "turno", no "Turno"
    turno = get_object_or_404(Turno, pk=pk) 
    
    if turno.status == 'PENDING':
        turno.status = 'CONFIRMED'
        turno.save()
        # ✅ CORRECCIÓN: usar .paciente.nombre
        messages.success(request, f"Turno N°{pk} de {turno.paciente.nombre} CONFIRMADO.")
    else:
        messages.warning(request, f"El turno N°{pk} ya está en estado: {turno.get_status_display()}.")

    return redirect('gestion_turnos')

@require_POST
def cancel_turno(request, pk):
    """Cancela un turno, liberando el slot para que esté disponible de nuevo."""
    turno = get_object_or_404(Turno, pk=pk)
    
    # Al cambiar el estado a CANCELLED, el slot de Fecha/Hora/Profesional se libera 
    if turno.status != 'CANCELLED':
        turno.status = 'CANCELLED'
        turno.save()
        # ✅ CORRECCIÓN: usar .paciente.nombre (y la variable era 'paciente', no 'patient')
        messages.success(request, f"Turno N°{pk} de {turno.paciente.nombre} CANCELADO y slot liberado.") 
    else:
        messages.warning(request, f"El turno N°{pk} ya estaba cancelado.")

    return redirect('gestion_turnos')
