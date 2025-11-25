from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm, EstadisticaPacienteForm, ObservacionForm, TestimonioForm, PerfilUpdateForm, InformeInterdisciplinarioForm, SeccionInformeForm
from .models import Entrevista, EstadoPaciente, Perfil, Paciente, Observacion, Testimonio, Turno, EstadisticaPaciente, InformeInterdisciplinario, SeccionInforme
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
    
    return render(request, 'mi_perfil.html', {
        'perfil': perfil
    })

def editar_perfil(request):
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

    return render(request, 'editar_perfil.html', {
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
            
        # Paso 3: FILTRAR LOS TURNOS y otros datos
        turnos = Turno.objects.filter(paciente=paciente_perfil).order_by('fecha')
        observaciones = Observacion.objects.filter(paciente=paciente_perfil).order_by('-fecha')[:5]
        
        # Obtener informes del paciente
        informes = InformeInterdisciplinario.objects.filter(paciente=paciente_perfil).prefetch_related('especialistas', 'secciones')[:5]

        # Calcular notificaciones (últimos 7 días)
        from datetime import timedelta
        from django.utils import timezone
        hace_7_dias = timezone.now() - timedelta(days=7)
        
        informes_nuevos = InformeInterdisciplinario.objects.filter(
            paciente=paciente_perfil,
            fecha_creacion__gte=hace_7_dias
        ).count()
        
        observaciones_nuevas = Observacion.objects.filter(
            paciente=paciente_perfil,
            fecha_registro__gte=hace_7_dias
        ).count()
        
        total_notificaciones = informes_nuevos + observaciones_nuevas
        
        notificaciones = []
        if informes_nuevos > 0:
            notificaciones.append(f"Tenés {informes_nuevos} informe{'s' if informes_nuevos > 1 else ''} nuevo{'s' if informes_nuevos > 1 else ''}")
        if observaciones_nuevas > 0:
            notificaciones.append(f"Tenés {observaciones_nuevas} observación{'es' if observaciones_nuevas > 1 else ''} nueva{'s' if observaciones_nuevas > 1 else ''}")

        context = {
            'paciente': paciente_perfil,
            'turnos': turnos,
            'observaciones': observaciones,
            'informes': informes,
            'total_notificaciones': total_notificaciones,
            'notificaciones': notificaciones,
            'informes_nuevos': informes_nuevos,
            'observaciones_nuevas': observaciones_nuevas,
        }
        
        return render(request, 'pacientes/dashboard_pacientes.html', context)

    except AttributeError:
        # El usuario no tiene un objeto 'perfil' asociado.
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('login') 
        
    except Exception as e:
        # Si hay un error en el filtro de Turnos 
        messages.error(request, f"Error al filtrar datos. Mensaje: {e}")
        return redirect('login')


@login_required
def paciente_turnos(request):
    return render(request, "pacientes/paciente_turnos.html")

@login_required
@solo_pacientes
def paciente_informes(request):
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        informes = InformeInterdisciplinario.objects.filter(
            paciente=perfil.paciente
        ).prefetch_related('especialistas', 'secciones').order_by('-fecha_informe')
        
        # Marcar los nuevos (últimos 7 días)
        from datetime import timedelta
        from django.utils import timezone
        hace_7_dias = timezone.now() - timedelta(days=7)
        
        for informe in informes:
            informe.es_nuevo = informe.fecha_creacion and informe.fecha_creacion >= hace_7_dias
        
        return render(request, "pacientes/paciente_informes.html", {
            'informes': informes
        })
    except Exception as e:
        messages.error(request, f"Error al cargar informes: {str(e)}")
        return redirect('dashboard_pacientes')

@login_required
def paciente_observaciones(request):
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        observaciones = Observacion.objects.filter(
            paciente=perfil.paciente
        ).order_by('-fecha')
        
        # Marcar las nuevas (últimos 7 días)
        from datetime import timedelta
        from django.utils import timezone
        hace_7_dias = timezone.now() - timedelta(days=7)
        
        for obs in observaciones:
            obs.es_nueva = obs.fecha_registro and obs.fecha_registro >= hace_7_dias
        
        return render(request, "pacientes/paciente_observaciones.html", {
            'observaciones': observaciones,
            'paciente': perfil.paciente
        })
    except:
        messages.error(request, "Error al cargar observaciones.")
        return redirect('dashboard_pacientes')

@login_required
def paciente_comprobantes(request):
    try:
        perfil = request.user.perfil
        if perfil.rol != 'paciente' or not perfil.paciente:
            messages.error(request, "Acceso no autorizado.")
            return redirect('login')
        
        # Por ahora solo renderizar el template
        # Cuando implementes comprobantes, aquí filtrarás por paciente
        return render(request, "pacientes/paciente_comprobantes.html", {
            'paciente': perfil.paciente
        })
    except:
        messages.error(request, "Error al cargar comprobantes.")
        return redirect('dashboard_pacientes')

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
                except AttributeError:
                    messages.error(request, "Tu cuenta no tiene un perfil asociado. Contacta al administrador.")
                    return redirect("login")

                # Redirigir según el rol del perfil
                if perfil.rol == "especialista":
                    return redirect("dashboard")  # Dashboard del Especialista

                elif perfil.rol == "paciente": 
                    return redirect("dashboard_pacientes")  # Dashboard de Pacientes
                
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
                    
                    # Verificar si ingresó el código de terapeuta
                    codigo_ingresado = form.cleaned_data.get("codigo_terapeuta", "").strip()
                    es_terapeuta = (codigo_ingresado == settings.CODIGO_SECRETO_TERAPEUTA)
                    
                    # Determinar el rol según el código
                    rol = "especialista" if es_terapeuta else "paciente"

                    # Crear perfil con los datos del formulario
                    perfil = Perfil.objects.create(
                        user=user,
                        nombre=form.cleaned_data.get("first_name", ""),
                        apellido=form.cleaned_data.get("last_name", ""),
                        dni=form.cleaned_data.get("dni", ""),
                        telefono=form.cleaned_data.get("telefono", ""),
                        email=form.cleaned_data.get("email", ""),
                        rol=rol
                    )

                    # Solo crear paciente si NO es terapeuta
                    if not es_terapeuta:
                        paciente_creado = Paciente.objects.create(
                            dni=perfil.dni,
                            nombre=perfil.nombre,
                            apellido=perfil.apellido,
                            fecha_nacimiento=form.cleaned_data.get("fecha_nacimiento"),
                            genero='O',
                            telefono=perfil.telefono,
                            email=perfil.email
                        )
                        # 🔗 ASOCIAR EL PACIENTE AL PERFIL
                        perfil.paciente = paciente_creado
                        perfil.save()

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
@solo_terapeutas
def dashboard(request):
    # Contar pacientes registrados
    total_pacientes = Paciente.objects.count()
    
    return render(request, 'dashboard.html', {
        'total_pacientes': total_pacientes
    })

def turnos_view(request):
    return render(request, 'turnos.html')

def gestionturnos(request):
    return render(request, 'gestionturnos.html')


@login_required
@solo_terapeutas
def pacientes_list(request):
    pacientes = Paciente.objects.all()
    return render(request, "pacientes/pacientes_list.html", {"pacientes": pacientes})


@login_required
@solo_terapeutas
def paciente_create(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes_list')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/pacientes_form.html', {'form': form})


@login_required
@solo_terapeutas
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

@login_required
@solo_terapeutas
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


@login_required
def editar_observacion(request, pk):
    """Editar una observación existente"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador o un especialista puede editar
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista' and observacion.creada_por != request.user:
            messages.error(request, "No tienes permiso para editar esta observación.")
            return redirect('lista_observaciones')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_observaciones')
    
    if request.method == 'POST':
        form = ObservacionForm(request.POST, instance=observacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Observación actualizada exitosamente.')
            return redirect('lista_observaciones')
    else:
        form = ObservacionForm(instance=observacion)
    
    return render(request, 'observaciones/observacion_form.html', {
        'form': form,
        'es_edicion': True,
        'observacion': observacion
    })


@login_required
def eliminar_observacion(request, pk):
    """Eliminar una observación"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador o un especialista puede eliminar
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista' and observacion.creada_por != request.user:
            messages.error(request, "No tienes permiso para eliminar esta observación.")
            return redirect('lista_observaciones')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_observaciones')
    
    if request.method == 'POST':
        observacion.delete()
        messages.success(request, 'Observación eliminada exitosamente.')
        return redirect('lista_observaciones')
    
    return render(request, 'observaciones/observacion_confirm_delete.html', {
        'observacion': observacion
    })

def comprobantes_view(request):
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    return render(request, 'comprobantes.html', {'pacientes': pacientes})

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

def editar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    if request.method == 'POST':
        form = TestimonioForm(request.POST, request.FILES, instance=testimonio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonio actualizado exitosamente.')
            return redirect('testimonios_lista')
    else:
        form = TestimonioForm(instance=testimonio)
    
    return render(request, 'testimonio/editar_testimonio.html', {
        'form': form,
        'testimonio': testimonio
    })

def eliminar_testimonio(request, id):
    testimonio = get_object_or_404(Testimonio, id=id)
    if request.method == 'POST':
        testimonio.delete()
        messages.success(request, 'Testimonio eliminado exitosamente.')
        return redirect('testimonios_lista')
    return render(request, 'testimonio/eliminar_testimonio.html', {
        'testimonio': testimonio
    })

def testimonios_inicio(request):
    testimonios = Testimonio.objects.filter(
        estado='aprobado',   
        publicado=True
    ).order_by('-fecha_envio')

    return render(request, 'testimonio/test_public.html', {'testimonios': testimonios})

@login_required
def crear_informe_interdisciplinario(request):
    """Crear un nuevo informe interdisciplinario"""
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.creado_por = request.user
            informe.save()
            form.save_m2m()  # Guardar relación ManyToMany de especialistas
            messages.success(request, f'Informe creado exitosamente para {informe.paciente}')
            return redirect('lista_informes')
    else:
        form = InformeInterdisciplinarioForm()

    return render(request, 'informes/crear_informe.html', {'form': form})


@login_required
@solo_terapeutas
def lista_informes(request):
    """Lista todos los informes interdisciplinarios (solo especialistas)"""
    informes = InformeInterdisciplinario.objects.all().prefetch_related('especialistas', 'paciente').order_by('-fecha_informe')
    return render(request, 'informes/lista_informes.html', {'informes': informes})


@login_required
def detalle_informe(request, informe_id):
    """Ver detalle de un informe con todas las secciones de los especialistas"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Verificar permisos
    try:
        perfil = request.user.perfil
        
        # Pacientes solo pueden ver sus propios informes
        if perfil.rol == 'paciente':
            if not perfil.paciente or informe.paciente != perfil.paciente:
                messages.error(request, "No tienes permiso para ver este informe.")
                return redirect('paciente_informes')
            
            # Obtener secciones para pacientes
            secciones = informe.secciones.all().select_related('especialista')
            
            context = {
                'informe': informe,
                'secciones': secciones,
            }
            
            # Usar template de pacientes
            return render(request, 'pacientes/detalle_informe_paciente.html', context)
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Obtener todas las secciones del informe (para especialistas)
    secciones = informe.secciones.all().select_related('especialista')
    
    # Verificar si el usuario actual es colaborador y si ya tiene una sección
    es_colaborador = False
    tiene_seccion = False
    
    if perfil.rol == 'especialista':
        es_colaborador = informe.especialistas.filter(pk=perfil.pk).exists()
        tiene_seccion = secciones.filter(especialista=perfil).exists()
    
    context = {
        'informe': informe,
        'secciones': secciones,
        'es_colaborador': es_colaborador,
        'tiene_seccion': tiene_seccion,
    }
    
    return render(request, 'informes/detalle_informe.html', context)


@login_required
def agregar_seccion_informe(request, informe_id):
    """Permite a un especialista agregar o editar su sección en el informe"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    try:
        perfil = request.user.perfil
        
        # Solo especialistas pueden agregar secciones
        if perfil.rol != 'especialista':
            messages.error(request, "Solo especialistas pueden agregar contenido a los informes.")
            return redirect('detalle_informe', informe_id=informe_id)
        
        # Verificar que sea un colaborador del informe
        if not informe.especialistas.filter(pk=perfil.pk).exists():
            messages.error(request, "No eres colaborador de este informe.")
            return redirect('detalle_informe', informe_id=informe_id)
        
        # Buscar si ya tiene una sección creada
        seccion, created = SeccionInforme.objects.get_or_create(
            informe=informe,
            especialista=perfil
        )
        
        if request.method == 'POST':
            form = SeccionInformeForm(request.POST, instance=seccion)
            if form.is_valid():
                form.save()
                action = "agregada" if created else "actualizada"
                messages.success(request, f'Tu sección ha sido {action} exitosamente.')
                return redirect('detalle_informe', informe_id=informe_id)
        else:
            form = SeccionInformeForm(instance=seccion)
        
        context = {
            'form': form,
            'informe': informe,
            'es_edicion': not created
        }
        
        return render(request, 'informes/agregar_seccion.html', context)
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')


@login_required
def editar_informe(request, informe_id):
    """Editar un informe interdisciplinario (solo el creador)"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Solo el creador puede editar el informe base
    if informe.creado_por != request.user:
        messages.error(request, "Solo el creador puede editar este informe.")
        return redirect('detalle_informe', informe_id=informe_id)
    
    if request.method == 'POST':
        form = InformeInterdisciplinarioForm(request.POST, instance=informe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informe actualizado exitosamente.')
            return redirect('detalle_informe', informe_id=informe_id)
    else:
        form = InformeInterdisciplinarioForm(instance=informe)
    
    return render(request, 'informes/editar_informe.html', {
        'form': form,
        'informe': informe
    })


@login_required
def eliminar_informe(request, informe_id):
    """Eliminar un informe (solo el creador)"""
    informe = get_object_or_404(InformeInterdisciplinario, pk=informe_id)
    
    # Solo el creador puede eliminar
    if informe.creado_por != request.user:
        messages.error(request, "Solo el creador puede eliminar este informe.")
        return redirect('lista_informes')
    
    if request.method == 'POST':
        paciente_nombre = str(informe.paciente)
        informe.delete()
        messages.success(request, f'Informe de {paciente_nombre} eliminado exitosamente.')
        return redirect('lista_informes')
    
    return render(request, 'informes/informe_confirm_delete.html', {
        'informe': informe
    })


@login_required
def eliminar_seccion_informe(request, seccion_id):
    """Eliminar una sección de informe (solo el autor de la sección)"""
    seccion = get_object_or_404(SeccionInforme, pk=seccion_id)
    
    try:
        perfil = request.user.perfil
        
        # Solo el autor de la sección puede eliminarla
        if seccion.especialista != perfil:
            messages.error(request, "Solo puedes eliminar tus propias secciones.")
            return redirect('detalle_informe', informe_id=seccion.informe.id)
        
        informe_id = seccion.informe.id
        
        if request.method == 'POST':
            seccion.delete()
            messages.success(request, 'Tu sección ha sido eliminada.')
            return redirect('detalle_informe', informe_id=informe_id)
        
        return render(request, 'informes/seccion_confirm_delete.html', {
            'seccion': seccion
        })
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_informes')