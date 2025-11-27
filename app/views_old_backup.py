from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
# Importar todas las clases de formularios desde forms.py
from .forms import LoginForm, RegisterForm, EntrevistaForm, PacienteForm, EstadisticaPacienteForm, ObservacionForm, TestimonioForm, PerfilUpdateForm, InformeInterdisciplinarioForm, TurnoFormGestion, SeccionInformeForm
from .models import Entrevista, EstadoPaciente, Perfil, Paciente, Observacion, Testimonio, Turno, EstadisticaPaciente, Especialista, STATUS_CHOICES, InformeInterdisciplinario, SeccionInforme, Contacto
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
from django.views.decorators.http import require_http_methods
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
    # Procesar formulario de contacto si se envía
    if request.method == 'POST' and 'nombre' in request.POST:
        Contacto.objects.create(
            nombre=request.POST.get('nombre'),
            email=request.POST.get('email'),
            telefono=request.POST.get('telefono', ''),
            mensaje=request.POST.get('mensaje', '')
        )
        messages.success(request, '¡Gracias por contactarnos! Te responderemos pronto.')
        return redirect('/#contacto')
    
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


# Vista para mostrar y procesar la Entrevista
def entrevista_view(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            dni_paciente = request.POST.get('dni_paciente', '').strip()
            nombre_paciente = request.POST.get('nombre_paciente', '').strip()
            apellido_paciente = request.POST.get('apellido_paciente', '').strip()
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            telefono = request.POST.get('telefono_contacto', '').strip()
            
            # Recopilar información adicional (pasos 2, 3, 4)
            datos_prenatales = request.POST.get('datos_prenatales', '')
            datos_escolares = request.POST.get('datos_escolares', '')
            datos_clinicos = request.POST.get('datos_clinicos', '')
            
            # Combinar motivo de consulta con todos los datos
            motivo_consulta = f"""
DATOS DEL TUTOR:
{request.POST.get('nombre_tutor', '')}
Teléfono: {telefono}

ETAPA PRENATAL Y PERINATAL:
{datos_prenatales}

ETAPA ESCOLAR:
{datos_escolares}

ANTECEDENTES CLÍNICOS:
{datos_clinicos}
            """.strip()
            
            # Validación de DNI (8 dígitos)
            if not re.match(r'^\d{8}$', dni_paciente):
                messages.error(request, "El DNI debe contener exactamente 8 dígitos numéricos.")
                return redirect('entrevista')
            
            # Validación básica
            if not all([dni_paciente, nombre_paciente, apellido_paciente]):
                messages.error(request, "Por favor complete todos los campos obligatorios del paso 1.")
                return redirect('entrevista')
            
            # Buscar o crear paciente
            paciente, created = Paciente.objects.get_or_create(
                dni=dni_paciente,
                defaults={
                    'nombre': nombre_paciente,
                    'apellido': apellido_paciente,
                    'fecha_nacimiento': fecha_nacimiento if fecha_nacimiento else None,
                    'telefono': telefono
                }
            )
            
            # Si el paciente ya existe, actualizar sus datos
            if not created:
                paciente.nombre = nombre_paciente
                paciente.apellido = apellido_paciente
                if fecha_nacimiento:
                    paciente.fecha_nacimiento = fecha_nacimiento
                if telefono:
                    paciente.telefono = telefono
                paciente.save()
            
            # Crear la entrevista (fecha y hora se asignarán después por los especialistas)
            from datetime import date, time
            entrevista = Entrevista.objects.create(
                paciente=paciente,
                fecha=date.today(),  # Fecha de recepción
                hora=time(9, 0),  # Hora por defecto, se modificará luego
                motivo_consulta=motivo_consulta
            )
            
            messages.success(request, f"¡Entrevista de admisión recibida correctamente! Gracias {nombre_paciente} {apellido_paciente}. Nuestros especialistas revisarán la información y nos pondremos en contacto para confirmar la cita y asignar el profesional más adecuado.")
            return redirect('index')
            
        except Exception as e:
            messages.error(request, f"Error al procesar la entrevista: {str(e)}")
            return redirect('entrevista')
    else:
        # Mostrar el formulario wizard cuando se accede por GET
        return render(request, 'entrevista_publica.html')


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

@login_required
def turnos_view(request):
    """Redirige a la nueva gestión de turnos"""
    return redirect('gestion_turnos')

@login_required
def gestionturnos(request):
    """Redirige a la nueva gestión de turnos"""
    return redirect('gestion_turnos')


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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Prellenar especialista con el usuario actual
        try:
            perfil = self.request.user.perfil
            # Buscar el valor del especialista basado en el perfil
            for choice_value, choice_label in Observacion.ESPECIALISTAS:
                if perfil.nombre.lower() in choice_label.lower() or perfil.apellido.lower() in choice_label.lower():
                    form.fields['especialista'].initial = choice_value
                    break
        except:
            pass
        return form

    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        # Asegurar que el especialista sea el del usuario actual
        try:
            perfil = self.request.user.perfil
            for choice_value, choice_label in Observacion.ESPECIALISTAS:
                if perfil.nombre.lower() in choice_label.lower() or perfil.apellido.lower() in choice_label.lower():
                    form.instance.especialista = choice_value
                    break
        except:
            pass
        return super().form_valid(form)


@login_required
def editar_observacion(request, pk):
    """Editar una observación existente"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador puede editar
    if observacion.creada_por != request.user:
        messages.error(request, "Solo el especialista que creó esta observación puede editarla.")
        return redirect('lista_observaciones')
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden editar observaciones.")
            return redirect('lista_observaciones')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('lista_observaciones')
    
    if request.method == 'POST':
        form = ObservacionForm(request.POST, instance=observacion)
        if form.is_valid():
            # Forzar que el especialista siga siendo el mismo (del creador original)
            observacion_actualizada = form.save(commit=False)
            # Mantener el especialista original, no permitir cambios
            observacion_actualizada.especialista = observacion.especialista
            observacion_actualizada.save()
            messages.success(request, 'Observación actualizada exitosamente.')
            return redirect('lista_observaciones')
    else:
        form = ObservacionForm(instance=observacion)
        # Prellenar y deshabilitar el campo especialista
        form.fields['especialista'].initial = observacion.especialista
    
    return render(request, 'observaciones/observacion_form.html', {
        'form': form,
        'es_edicion': True,
        'observacion': observacion
    })


@login_required
def eliminar_observacion(request, pk):
    """Eliminar una observación"""
    observacion = get_object_or_404(Observacion, pk=pk)
    
    # Solo el creador puede eliminar
    if observacion.creada_por != request.user:
        messages.error(request, "Solo el especialista que creó esta observación puede eliminarla.")
        return redirect('lista_observaciones')
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden eliminar observaciones.")
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
    especialistas = Especialista.objects.all()
    
    # Preparar turnos como JSON para el frontend
    import json
    from datetime import date
    
    turnos_json = json.dumps([{
        'id': t.id,
        'paciente': t.paciente.nombre + ' ' + t.paciente.apellido,
        'paciente_id': t.paciente.id,
        'especialista': t.especialista.nombre,
        'especialista_id': t.especialista.id,
        'fecha': t.fecha.strftime('%Y-%m-%d'),
        'hora': t.hora.strftime('%H:%M'),
        'motivo': t.motivo,
        'status': t.status
    } for t in turnos])
    
    pacientes_json = json.dumps([{
        'id': p.id,
        'nombre': p.nombre,
        'apellido': p.apellido,
        'dni_paciente': p.dni
    } for p in pacientes])
    
    especialistas_json = json.dumps([{
        'id': e.id,
        'nombre': e.nombre,
        'especialidad': e.especialidad
    } for e in especialistas])
    
    context = {
        'turnos': turnos,
        'especialistas': especialistas,  # QuerySet para el template
        'pacientes': pacientes_json,
        'especialistas_json': especialistas_json,
        'turnos_json': turnos_json,
        'status_choices': STATUS_CHOICES,
        'today': date.today().strftime('%Y-%m-%d')
    }
    
    return render(request, 'turnos/gestion_turnos.html', context)


@login_required
@csrf_exempt
def crear_turno(request):
    """Crear un nuevo turno"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        # Validar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no autenticado'
            })
        
        # Validar que el usuario sea especialista
        try:
            perfil = request.user.perfil
        except AttributeError:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no tiene perfil asociado'
            })
        
        if perfil.rol != 'especialista':
            return JsonResponse({
                'success': False,
                'error': 'Solo los especialistas pueden crear turnos'
            })
        
        # Buscar o crear el Especialista asociado al perfil
        especialista_usuario, created = Especialista.objects.get_or_create(
            perfil=perfil,
            defaults={
                'nombre': f"{perfil.nombre} {perfil.apellido}",
                'especialidad': perfil.especialidad or "No especificado",
                'matricula': perfil.matricula,
                'email': perfil.email,
                'telefono': perfil.telefono
            }
        )
        
        import json
        import re
        data = json.loads(request.body)
        
        # Buscar o crear paciente por DNI
        dni = data.get('dni_paciente', '').strip()
        nombre = data.get('nombre_paciente', '').strip()
        apellido = data.get('apellido_paciente', '').strip()
        
        if not dni or not nombre or not apellido:
            return JsonResponse({
                'success': False, 
                'error': 'DNI, nombre y apellido son obligatorios'
            })
        
        # Validar que el DNI tenga exactamente 8 dígitos
        if not re.match(r'^\d{8}$', dni):
            return JsonResponse({
                'success': False,
                'error': 'El DNI debe contener exactamente 8 dígitos numéricos'
            })
        
        # Buscar paciente existente o crear nuevo
        paciente, created = Paciente.objects.get_or_create(
            dni=dni,
            defaults={'nombre': nombre, 'apellido': apellido}
        )
        
        # Si ya existe pero con diferente nombre, actualizamos
        if not created:
            if paciente.nombre != nombre or paciente.apellido != apellido:
                paciente.nombre = nombre
                paciente.apellido = apellido
                paciente.save()
        
        # USAR EL ESPECIALISTA DEL USUARIO ACTUAL (no permitir selección)
        especialista = especialista_usuario
        fecha = data.get('fecha')
        
        # Validar que el paciente no tenga otro turno con el mismo especialista el mismo día
        turno_existente = Turno.objects.filter(
            paciente=paciente,
            especialista=especialista,
            fecha=fecha
        ).exclude(status='CANCELLED').first()
        
        if turno_existente:
            return JsonResponse({
                'success': False,
                'error': f'El paciente ya tiene un turno contigo el {fecha} a las {turno_existente.hora.strftime("%H:%M")}. No se pueden agendar múltiples turnos con el mismo profesional en un mismo día.'
            })
        
        # Crear el turno
        turno = Turno(
            paciente=paciente,
            especialista=especialista,
            fecha=fecha,
            hora=data.get('hora'),
            motivo=data.get('motivo', ''),
            creado_por=request.user
        )
        
        turno.full_clean()  # Validar
        turno.save()
        
        print(f"✅ TURNO GUARDADO: ID={turno.id}, Paciente={turno.paciente}, Fecha={turno.fecha}, Hora={turno.hora}")
        
        return JsonResponse({
            'success': True,
            'message': 'Turno creado exitosamente',
            'turno': {
                'id': turno.id,
                'paciente': f"{turno.paciente.nombre} {turno.paciente.apellido}",
                'paciente_dni': turno.paciente.dni,
                'especialista': turno.especialista.nombre,
                'fecha': turno.fecha.strftime('%Y-%m-%d'),
                'hora': turno.hora.strftime('%H:%M'),
                'motivo': turno.motivo,
                'status': turno.get_status_display()
            }
        })
        
    except Especialista.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'El profesional seleccionado no existe'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Error al parsear los datos JSON'
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def editar_turno(request, pk):
    """Editar un turno existente"""
    turno = get_object_or_404(Turno, pk=pk)
    
    # Validar que el usuario sea el creador del turno
    if turno.creado_por and turno.creado_por != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Solo el especialista que creó este turno puede editarlo'
        })
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            return JsonResponse({
                'success': False,
                'error': 'Solo los especialistas pueden editar turnos'
            })
    except:
        return JsonResponse({
            'success': False,
            'error': 'Usuario no tiene perfil de especialista'
        })
    
    if request.method == 'POST':
        try:
            import json
            import re
            data = json.loads(request.body)
            
            # Buscar o crear paciente por DNI (igual que en crear_turno)
            dni = data.get('dni_paciente', '').strip()
            nombre = data.get('nombre_paciente', '').strip()
            apellido = data.get('apellido_paciente', '').strip()
            
            if not dni or not nombre or not apellido:
                return JsonResponse({
                    'success': False, 
                    'error': 'DNI, nombre y apellido son obligatorios'
                })
            
            # Validar que el DNI tenga exactamente 8 dígitos
            if not re.match(r'^\d{8}$', dni):
                return JsonResponse({
                    'success': False,
                    'error': 'El DNI debe contener exactamente 8 dígitos numéricos'
                })
            
            # Buscar paciente existente o crear nuevo
            paciente, created = Paciente.objects.get_or_create(
                dni=dni,
                defaults={'nombre': nombre, 'apellido': apellido}
            )
            
            # Si ya existe pero con diferente nombre, actualizamos
            if not created:
                if paciente.nombre != nombre or paciente.apellido != apellido:
                    paciente.nombre = nombre
                    paciente.apellido = apellido
                    paciente.save()
            
            # Obtener especialista
            especialista_id = data.get('especialista')
            if not especialista_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe seleccionar un profesional'
                })
            
            especialista = Especialista.objects.get(id=especialista_id)
            fecha = data.get('fecha')
            
            # Validar que el paciente no tenga otro turno con el mismo especialista el mismo día (excepto el turno actual)
            turno_existente = Turno.objects.filter(
                paciente=paciente,
                especialista=especialista,
                fecha=fecha
            ).exclude(id=turno.id).exclude(status='CANCELLED').first()
            
            if turno_existente:
                return JsonResponse({
                    'success': False,
                    'error': f'El paciente ya tiene un turno con {especialista.nombre} el {fecha} a las {turno_existente.hora.strftime("%H:%M")}. No se pueden agendar múltiples turnos con el mismo profesional en un mismo día.'
                })
            
            # Actualizar el turno
            turno.paciente = paciente
            turno.especialista = especialista
            turno.fecha = data.get('fecha')
            turno.hora = data.get('hora')
            turno.motivo = data.get('motivo', '')
            
            turno.full_clean()  # Validar
            turno.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Turno modificado exitosamente'
            })
            
        except Especialista.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'El profesional seleccionado no existe'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def confirmar_turno(request, pk):
    """Confirmar un turno pendiente"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        
        if turno.status == 'PENDING':
            turno.status = 'CONFIRMED'
            turno.save()
            messages.success(request, f"Turno N°{pk} de {turno.paciente.nombre} confirmado.")
            return JsonResponse({'success': True, 'message': 'Turno confirmado'})
        else:
            return JsonResponse({'success': False, 'error': f"El turno ya está en estado: {turno.get_status_display()}"})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def cancelar_turno(request, pk):
    """Cancelar un turno (libera el horario)"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        
        if turno.status != 'CANCELLED':
            turno.status = 'CANCELLED'
            turno.save()
            messages.success(request, f"Turno N°{pk} de {turno.paciente.nombre} cancelado. Horario liberado.")
            return JsonResponse({'success': True, 'message': 'Turno cancelado y horario liberado'})
        else:
            return JsonResponse({'success': False, 'error': 'El turno ya estaba cancelado'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def eliminar_turno(request, pk):
    """Eliminar permanentemente un turno"""
    if request.method == 'POST':
        turno = get_object_or_404(Turno, pk=pk)
        
        # Validar que el usuario sea el creador del turno
        if turno.creado_por and turno.creado_por != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Solo el especialista que creó este turno puede eliminarlo'
            })
        
        # Validar que el usuario sea especialista
        try:
            perfil = request.user.perfil
            if perfil.rol != 'especialista':
                return JsonResponse({
                    'success': False,
                    'error': 'Solo los especialistas pueden eliminar turnos'
                })
        except:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no tiene perfil de especialista'
            })
        
        paciente_nombre = turno.paciente.nombre
        
        try:
            turno.delete()
            messages.success(request, f"Turno N°{pk} de {paciente_nombre} eliminado permanentemente.")
            return JsonResponse({'success': True, 'message': 'Turno eliminado exitosamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ========== GESTIÓN DE ENTREVISTAS DE ADMISIÓN ===
@login_required
def gestion_entrevistas(request):
    """Vista para que los especialistas gestionen las entrevistas de admisión"""
    entrevistas = Entrevista.objects.select_related('paciente', 'especialista_asignado').order_by('-fecha_creacion')
    especialistas = Especialista.objects.all()
    
    # Contar por estado
    total = entrevistas.count()
    pendientes = entrevistas.filter(estado='pendiente').count()
    en_revision = entrevistas.filter(estado='en_revision').count()
    derivadas = entrevistas.filter(estado='derivada').count()
    
    context = {
        'entrevistas': entrevistas,
        'especialistas': especialistas,
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'derivadas': derivadas,
    }
    
    return render(request, 'entrevistas/gestion_entrevistas.html', context)


@login_required
def ver_entrevista(request, pk):
    """Ver detalles completos de una entrevista"""
    entrevista = get_object_or_404(Entrevista, pk=pk)
    especialistas = Especialista.objects.all()
    
    context = {
        'entrevista': entrevista,
        'especialistas': especialistas,
    }
    
    return render(request, 'entrevistas/ver_entrevista.html', context)


@login_required
def derivar_entrevista(request, pk):
    """Asignar especialista y cambiar estado de entrevista"""
    if request.method == 'POST':
        try:
            entrevista = get_object_or_404(Entrevista, pk=pk)
            data = json.loads(request.body)
            
            especialista_id = data.get('especialista_id')
            estado = data.get('estado')
            observaciones = data.get('observaciones', '')
            
            if especialista_id:
                especialista = Especialista.objects.get(id=especialista_id)
                entrevista.especialista_asignado = especialista
            
            if estado:
                entrevista.estado = estado
            
            if observaciones:
                entrevista.observaciones = observaciones
            
            entrevista.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Entrevista actualizada correctamente'
            })
            
        except Especialista.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'El especialista seleccionado no existe'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==================== INFORMES INTERDISCIPLINARIOS =============
@login_required
def crear_informe_interdisciplinario(request):
    """Crear un nuevo informe interdisciplinario"""
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden crear informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
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
def lista_informes(request):
    """Lista todos los informes (especialistas ven todos, pacientes ven solo los suyos)"""
    try:
        perfil = request.user.perfil
        
        if perfil.rol == 'especialista':
            # Especialistas ven todos los informes o los que colaboran
            informes = InformeInterdisciplinario.objects.all().prefetch_related('especialistas', 'paciente')
        else:
            # Pacientes ven solo sus informes
            if perfil.paciente:
                informes = InformeInterdisciplinario.objects.filter(paciente=perfil.paciente).prefetch_related('especialistas')
            else:
                informes = []
                messages.info(request, "No tienes informes asociados.")
        
        return render(request, 'informes/lista_informes.html', {'informes': informes})
    
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')


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
    # Obtener todas las secciones del informe
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
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden editar informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Solo el creador puede editar el informe base
    if informe.creado_por != request.user:
        messages.error(request, "Solo el especialista que creó este informe puede editarlo.")
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
    
    # Validar que el usuario sea especialista
    try:
        perfil = request.user.perfil
        if perfil.rol != 'especialista':
            messages.error(request, "Solo los especialistas pueden eliminar informes.")
            return redirect('dashboard')
    except AttributeError:
        messages.error(request, "Error: Tu cuenta no tiene un perfil asociado.")
        return redirect('dashboard')
    
    # Solo el creador puede eliminar
    if informe.creado_por != request.user:
        messages.error(request, "Solo el especialista que creó este informe puede eliminarlo.")
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


# ============== GESTIÓN DE TURNOS ==============

@login_required
@solo_terapeutas
def gestion_turnos(request):
    """Vista principal para gestionar turnos"""
    from datetime import date
    import json
    
    turnos = Turno.objects.all().select_related('paciente', 'especialista').order_by('-fecha', '-hora')
    especialistas = Especialista.objects.all()
    
    # Obtener o crear el Especialista del usuario actual
    especialista_usuario = None
    try:
        perfil = request.user.perfil
        if perfil.rol == 'especialista':
            especialista_usuario, created = Especialista.objects.get_or_create(
                perfil=perfil,
                defaults={
                    'nombre': f"{perfil.nombre} {perfil.apellido}",
                    'especialidad': perfil.especialidad or "No especificado",
                    'matricula': perfil.matricula,
                    'email': perfil.email,
                    'telefono': perfil.telefono
                }
            )
            # Filtrar turnos solo del especialista actual
            turnos = turnos.filter(especialista=especialista_usuario)
    except:
        pass
    
    # Preparar turnos como JSON para JavaScript
    turnos_json = json.dumps([
        {
            'id': t.id,
            'fecha': t.fecha.strftime('%Y-%m-%d'),
            'hora': t.hora.strftime('%H:%M'),
            'especialista_id': t.especialista.id,
            'status': t.status,
            'motivo': t.motivo or ''
        }
        for t in turnos
    ])
    
    context = {
        'turnos': turnos,
        'especialistas': especialistas,
        'especialista_usuario': especialista_usuario,
        'status_choices': STATUS_CHOICES,
        'turnos_json': turnos_json,
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'Turnos/gestion_turnos.html', context)

@login_required
@solo_terapeutas
def editar_turno(request, pk):
    """Editar un turno existente"""
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        form = TurnoFormGestion(request.POST, instance=turno)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Turno actualizado exitosamente')
                return redirect('gestion_turnos')
            except Exception as e:
                messages.error(request, f'Error al actualizar el turno: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = TurnoFormGestion(instance=turno)
    
    return render(request, 'Turnos/gestion_turnos.html', {
        'form': form,
        'turno_edit': turno,
        'turnos': Turno.objects.all().select_related('paciente', 'especialista').order_by('-fecha', '-hora'),
        'especialistas': Especialista.objects.all(),
        'status_choices': STATUS_CHOICES,
    })

@login_required
@solo_terapeutas
def confirmar_turno(request, pk):
    """Confirmar un turno"""
    turno = get_object_or_404(Turno, pk=pk)
    turno.status = 'CONFIRMED'
    turno.save()
    messages.success(request, f'Turno confirmado para {turno.paciente.nombre} {turno.paciente.apellido}')
    return redirect('gestion_turnos')

@login_required
@solo_terapeutas
def cancelar_turno(request, pk):
    """Cancelar un turno"""
    turno = get_object_or_404(Turno, pk=pk)
    turno.status = 'CANCELLED'
    turno.save()
    messages.warning(request, f'Turno cancelado para {turno.paciente.nombre} {turno.paciente.apellido}')
    return redirect('gestion_turnos')

@login_required
@solo_terapeutas
def eliminar_turno(request, pk):
    """Eliminar un turno"""
    turno = get_object_or_404(Turno, pk=pk)
    paciente_nombre = f"{turno.paciente.nombre} {turno.paciente.apellido}"
    turno.delete()
    messages.success(request, f'Turno eliminado para {paciente_nombre}')
    return redirect('gestion_turnos')


# ============== GESTIÓN DE ENTREVISTAS ==============

@login_required
@solo_terapeutas
def gestion_entrevistas(request):
    """Vista para gestionar entrevistas de admisión"""
    entrevistas = Entrevista.objects.all().select_related('paciente', 'especialista_asignado').order_by('-fecha', '-hora')
    especialistas = Especialista.objects.all()
    
    context = {
        'entrevistas': entrevistas,
        'especialistas': especialistas,
    }
    return render(request, 'entrevistas/gestion_entrevistas.html', context)

@login_required
@solo_terapeutas
def ver_entrevista(request, pk):
    """Ver detalles de una entrevista"""
    entrevista = get_object_or_404(Entrevista, pk=pk)
    especialistas = Especialista.objects.all()
    
    context = {
        'entrevista': entrevista,
        'especialistas': especialistas,
    }
    return render(request, 'entrevistas/ver_entrevista.html', context)

@login_required
@solo_terapeutas
def derivar_entrevista(request, pk):
    """Derivar una entrevista a un especialista"""
    if request.method == 'POST':
        entrevista = get_object_or_404(Entrevista, pk=pk)
        especialista_id = request.POST.get('especialista_id')
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '')
        
        if especialista_id:
            especialista = get_object_or_404(Especialista, pk=especialista_id)
            entrevista.especialista_asignado = especialista
        
        if nuevo_estado:
            entrevista.estado = nuevo_estado
        
        if observaciones:
            entrevista.observaciones = observaciones
        
        entrevista.save()
        messages.success(request, 'Entrevista actualizada exitosamente')
        return redirect('gestion_entrevistas')
    
    return redirect('ver_entrevista', pk=pk)


# ============== GESTIÓN DE CONTACTOS ==============

@login_required
@solo_terapeutas
def lista_contactos(request):
    """Vista para ver todos los contactos recibidos"""
    contactos = Contacto.objects.all().order_by('-fecha_envio')
    
    # Contar por estado
    total = contactos.count()
    nuevos = contactos.filter(estado='nuevo').count()
    leidos = contactos.filter(estado='leido').count()
    respondidos = contactos.filter(estado='respondido').count()
    
    context = {
        'contactos': contactos,
        'total': total,
        'nuevos': nuevos,
        'leidos': leidos,
        'respondidos': respondidos,
    }
    
    return render(request, 'contactos/lista_contactos.html', context)


@login_required
@solo_terapeutas
def marcar_contacto_leido(request, pk):
    """Marcar un contacto como leído"""
    contacto = get_object_or_404(Contacto, pk=pk)
    contacto.estado = 'leido'
    contacto.save()
    messages.success(request, 'Contacto marcado como leído')
    return redirect('lista_contactos')


@login_required
@solo_terapeutas
def marcar_contacto_respondido(request, pk):
    """Marcar un contacto como respondido"""
    contacto = get_object_or_404(Contacto, pk=pk)
    contacto.estado = 'respondido'
    contacto.save()
    messages.success(request, 'Contacto marcado como respondido')
    return redirect('lista_contactos')


    
    return redirect('ver_entrevista', pk=pk)
