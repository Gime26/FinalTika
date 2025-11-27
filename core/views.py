from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def politicas_privacidad(request):
    """Vista para mostrar las políticas de privacidad"""
    return render(request, 'politicas_privacidad.html')

def terminos_condiciones(request):
    """Vista para mostrar los términos y condiciones"""
    return render(request, 'terminos_condiciones.html')