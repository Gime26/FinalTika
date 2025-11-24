from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm, EstadisticaPacienteForm, ObservacionForm, TestimonioForm, PerfilUpdateForm, InformeInterdisciplinarioForm
from .models import Entrevista, EstadoPaciente, Perfil, Paciente, Observacion, Testimonio, Turno, EstadisticaPaciente
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib.auth import get_user_model 
from .decorators import solo_terapeutas, solo_pacientes
from django.conf import settings
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def mi_perfil(request):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado. Contacta a un administrador.")
        return redirect('login')
    
    advertencia = not perfil.matricula   # Si falta la matrícula, mostramos el aviso

    if request.method == 'POST':
        form = PerfilUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('mi_perfil')
            except IntegrityError:
                messages.error(request, "Error: El DNI ingresado ya está asociado a otra cuenta.")
            except Exception as e:
                messages.error(request, f"Error al actualizar perfil: {str(e)}")
        else:
            messages.error(request, "Por favor, verifica los datos ingresados.")
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
    testimonios = Testimonio.objects.filter(
        estado='aprobado',
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, "index.html", {
        "testimonios": testimonios
    })
@solo_terapeutas
def dashboard_terapeutas(request):
    return render(request, 'dashboard.html')

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
        turnos = Turno.objects.filter(paciente=paciente_perfil).order_by('fecha')

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
                except user.perfil.RelatedObjectDoesNotExist: # Usamos la excepción a nivel de descriptor de campo
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
            user = None
            try:
                with transaction.atomic():
                    # Crear el usuario
                    user = form.save()

                    # Crear perfil con los datos del formulario
                    perfil = Perfil.objects.create(
                        user=user,
                        nombre=form.cleaned_data.get("first_name", ""),
                        apellido=form.cleaned_data.get("last_name", ""),
                        dni=form.cleaned_data.get("dni") or form.cleaned_data.get("numero_documento", ""),
                        telefono=form.cleaned_data.get("telefono", ""),
                        email=form.cleaned_data.get("email", ""),
                        rol="paciente"
                    )

                    # Crear paciente asociado
                    Paciente.objects.create(
                        dni_paciente=perfil.dni,
                        nombre=perfil.nombre,
                        apellido=perfil.apellido,
                        telefono=perfil.telefono,
                        email=perfil.email
                    )

                messages.success(request, "Cuenta creada exitosamente. Por favor, inicia sesión.")
                return redirect("login")
            
            except IntegrityError as e:
                # Si hay error de integridad (DNI duplicado, etc.), eliminar el usuario creado
                if user and user.id:
                    try:
                        user.delete()
                    except:
                        pass
                
                if "dni" in str(e).lower() or "unique" in str(e).lower():
                    messages.error(request, "Ya existe un usuario con ese DNI. Por favor, intenta con otro.")
                else:
                    messages.error(request, f"Error al crear la cuenta: {str(e)}")
            
            except Exception as e:
                # Cleanup en caso de error inesperado
                if user and user.id:
                    try:
                        user.delete()
                    except:
                        pass
                messages.error(request, f"Error inesperado: {str(e)}")
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = RegisterForm()

    return render(request, "registro.html", {"form": form})

@login_required
def dashboard(request): 
    return render(request, 'dashboard.html')

def turnos_view(request):
    return render(request, 'turnos.html')

def gestionturnos(request):
    return render(request, 'gestionturnos.html')


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

    pacientes = EstadisticaPaciente.objects.all().order_by("-fecha_registro")
    total = pacientes.count()
    promedio_edad = pacientes.aggregate(prom=Avg("edad"))["prom"] or 0

    conteo = EstadisticaPaciente.objects.values("especialidad").annotate(total=Count("id"))

    return render(request, "estadistica.html", {
        "pacientes": pacientes,
        "total": total,
        "promedio": round(promedio_edad, 1),
        "conteo": list(conteo)
    })

@csrf_exempt
def estadistica_agregar(request):
    if request.method == "POST":
        data = json.loads(request.body)

        nombre = data.get("nombre")
        edad = data.get("edad")
        especialidad = data.get("especialidad")

        nuevo = EstadisticaPaciente.objects.create(
            nombre=nombre,
            edad=edad,
            especialidad=especialidad
        )

        return JsonResponse({"status": "ok", "id": nuevo.id})

    return JsonResponse({"error": "Método no permitido"}, status=400)
    return redirect('formulario_informe')


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
            testimonio.estado = "pendiente"     
            testimonio.publicado = False
            testimonio.save()
            return redirect('index')
    else:
        form = TestimonioForm()

    return render(request, 'testimonio/enviar_testimonio.html', {'form': form})

def testimonios_publicos(request):
    testimonios = Testimonio.objects.filter(
        estado='aprobado',   
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, 'testimonios_publicos.html', {'testimonios': testimonios})

def testimonios_lista(request):
    testimonios = Testimonio.objects.all().order_by('-fecha_envio')
    return render(request, 'dashboard/testimonios.html', {'testimonios': testimonios})

def aprobar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    testimonio.estado = 'aprobado'   # ✔ CORRECTO SEGÚN EL MODELO
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

def testimonios_inicio(request):
    testimonios = Testimonio.objects.filter(
        estado='aprobado',   
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})

def crear_informe_interdisciplinario(request):
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = InformeInterdisciplinarioForm()

    return render(request, 'salud/crear_informe_interdisciplinario.html', {'form': form})