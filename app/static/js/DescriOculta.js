// script.js
// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Selecciona todas las cajas de servicio
    const serviceBoxes = document.querySelectorAll('.box');

    // Itera sobre cada caja de servicio
    serviceBoxes.forEach(function(box) {
        // Añade un 'event listener' para el evento 'click' en cada caja
        box.addEventListener('click', function() {
            // Encuentra la descripción dentro de la caja actual que fue clickeada
            const description = this.querySelector('.descripcion-oculta');

            // Verifica el estado actual de la descripción y lo cambia
            if (description.style.display === 'none' || description.style.display === '') {
                description.style.display = 'block'; // Muestra la descripción
            } else {
                description.style.display = 'none'; // Oculta la descripción
            }
        });
    });
});