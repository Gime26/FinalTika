# Estructura de Templates - Index

El archivo `index.html` ahora está modularizado en componentes separados para facilitar el mantenimiento.

## Ubicación de los Parciales

Todos los componentes están en: `app/templates/partials/index/`

## Secciones Disponibles

### 1. **inicio.html**
- Sección de bienvenida
- Botones de Ingresar y Registrarse
- Editar para cambiar: textos de bienvenida, botones de call-to-action

### 2. **nosotros.html**
- Descripción del centro TIKA
- Valores principales (Aprender jugando, Vínculos de confianza, Acompañar a la familia)
- Editar para cambiar: descripción institucional, valores destacados

### 3. **servicios.html**
- Tarjetas de servicios terapéuticos
- Incluye: Psicología, Fonoaudiología, Kinesiología, Psicomotricidad, Psicopedagogía
- Editar para: agregar/quitar servicios, cambiar descripciones

### 4. **test.html**
- Sección de evaluaciones y entrevistas
- Botón "Realizar Entrevista"
- Editar para cambiar: texto descriptivo, enlaces

### 5. **equipo.html**
- Perfiles del equipo profesional
- Fotos y nombres de especialistas
- Editar para: agregar/quitar profesionales, actualizar información

### 6. **testimonios.html**
- Galería de testimonios publicados
- Botón "Enviar tu testimonio"
- Editar para cambiar: diseño de testimonios, botones

### 7. **contacto.html**
- Dirección física: Bolivar 142, Salta Capital
- Teléfono: 3875827499
- Mapa de ubicación
- Editar para cambiar: dirección, teléfono, mapa

### 8. **footer.html**
- Copyright y créditos
- Redes sociales (Facebook, Instagram)
- Editar para cambiar: enlaces de redes, texto del footer

## Cómo Editar

Para modificar cualquier sección:

1. Abrí el archivo correspondiente en `app/templates/partials/index/`
2. Realizá los cambios necesarios
3. Guardá el archivo
4. Recargá la página del index

**Ventaja:** Si algo se rompe, solo afecta a esa sección específica, no a toda la página.

## Ejemplo de Edición

Para cambiar el teléfono de contacto:
```
Archivo: app/templates/partials/index/contacto.html
Línea: <a href="#"><i class="fab fa-whatsapp"></i> 3875827499</a>
```

Para agregar un nuevo profesional al equipo:
```
Archivo: app/templates/partials/index/equipo.html
Duplicar el bloque <div class="team-member">...</div>
Actualizar foto, nombre y descripción
```

## Estructura del Index Principal

```html
{% include 'partials/index/inicio.html' %}
{% include 'partials/index/nosotros.html' %}
{% include 'partials/index/servicios.html' %}
{% include 'partials/index/test.html' %}
{% include 'partials/index/equipo.html' %}
{% include 'partials/index/testimonios.html' %}
{% include 'partials/index/contacto.html' %}
{% include 'partials/index/footer.html' %}
```

Cada `{% include %}` carga el contenido de su archivo parcial correspondiente.
