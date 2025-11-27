#!/usr/bin/env python
"""
Script para verificar que todas las vistas están presentes en los módulos
"""
import os

def verificar_funciones():
    """Verifica que todas las funciones están en los archivos correctos"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    views_dir = os.path.join(base_dir, 'views')
    
    # Mapeo de archivos y funciones esperadas
    modulos = {
        'auth_views.py': ['login_view', 'register_view', 'logout_view', 'base'],
        'perfil_views.py': ['mi_perfil', 'editar_perfil'],
        'dashboard_views.py': ['inicio', 'dashboard', 'dashboard_terapeutas'],
        'turno_views.py': ['gestion_turnos', 'crear_turno', 'editar_turno', 'confirmar_turno', 
                          'cancelar_turno', 'eliminar_turno', 'turnos_view', 'gestionturnos'],
        'paciente_views.py': ['pacientes_list', 'paciente_create', 'paciente_update', 'paciente_delete',
                             'dashboard_pacientes', 'paciente_turnos', 'paciente_informes',
                             'paciente_observaciones', 'paciente_comprobantes', 'paciente_perfil'],
        'observacion_views.py': ['ListaObservacionesView', 'CrearObservacionView',
                                'editar_observacion', 'eliminar_observacion'],
        'testimonio_views.py': ['enviar_testimonio', 'testimonios_publicos', 'testimonios_lista',
                               'aprobar_testimonio', 'restringir_testimonio', 'editar_testimonio',
                               'eliminar_testimonio', 'testimonios_inicio'],
        'contacto_views.py': ['lista_contactos', 'marcar_contacto_leido', 'marcar_contacto_respondido',
                             'confirmar_eliminar_contacto', 'eliminar_contacto'],
        'informe_views.py': ['crear_informe_interdisciplinario', 'lista_informes', 'detalle_informe',
                            'agregar_seccion_informe', 'editar_informe', 'eliminar_informe',
                            'eliminar_seccion_informe'],
        'entrevista_views.py': ['entrevista_view', 'gestion_entrevistas', 'ver_entrevista', 
                               'derivar_entrevista'],
        'estadistica_views.py': ['estadistica_view', 'estadistica_agregar'],
        'comprobantes_views.py': ['comprobantes_view'],
    }
    
    print("🔍 Verificando presencia de funciones en módulos...\n")
    
    total_funciones = 0
    funciones_encontradas = 0
    errores = []
    
    for modulo, funciones in modulos.items():
        archivo_path = os.path.join(views_dir, modulo)
        
        if not os.path.exists(archivo_path):
            print(f"❌ Archivo {modulo} NO EXISTE")
            errores.append(f"Archivo faltante: {modulo}")
            continue
        
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print(f"\n📄 {modulo}:")
        for funcion in funciones:
            total_funciones += 1
            # Buscar la definición de la función o clase
            if f"def {funcion}" in contenido or f"class {funcion}" in contenido:
                print(f"   ✅ {funcion}")
                funciones_encontradas += 1
            else:
                print(f"   ❌ {funcion} NO ENCONTRADA")
                errores.append(f"{modulo}: {funcion}")
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"{'='*60}")
    print(f"✅ Funciones encontradas: {funciones_encontradas}/{total_funciones}")
    print(f"❌ Funciones faltantes: {len(errores)}")
    
    if errores:
        print(f"\n⚠️  PROBLEMAS DETECTADOS:")
        for error in errores:
            print(f"   - {error}")
        return False
    else:
        print(f"\n🎉 ¡Todas las funciones están presentes!")
        
        # Verificar también el __init__.py
        init_file = os.path.join(views_dir, '__init__.py')
        if os.path.exists(init_file):
            print(f"\n✅ __init__.py existe")
            with open(init_file, 'r') as f:
                init_content = f.read()
            imports_esperados = len(modulos)
            imports_encontrados = sum(1 for m in modulos.keys() 
                                     if f"from .{m[:-3]} import" in init_content)
            print(f"✅ Imports en __init__.py: {imports_encontrados}/{imports_esperados}")
        
        return True

if __name__ == '__main__':
    try:
        resultado = verificar_funciones()
        exit(0 if resultado else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

