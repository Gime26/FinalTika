const container = document.querySelector('.container');
const btnSignIn = document.getElementById('btn-sign-in');
const btnSignUp = document.getElementById('btn-sign-up');
const modal = document.getElementById('modalTurnos');
const btnTurnos = document.getElementById('btnTurnos'); // botón de Turnos
const opcionesDashboard = document.getElementById('opcionesDashboard'); // contenedor con todas las opciones
const spanClose = document.querySelector('.modal .close');

btnSignUp.addEventListener('click', () => {
    container.classList.add('toggle');
});

btnSignIn.addEventListener('click', () => {
    container.classList.remove('toggle');
});

// Opcional: Para manejar la visibilidad de los mensajes de bienvenida en móvil
// dependiendo de la clase 'toggle'
const welcomeSignIn = document.querySelector('.welcome-sign-in');
const welcomeSignUp = document.querySelector('.welcome-sign-up');

function updateWelcomeVisibility() {
    if (window.innerWidth <= 768) { // Si es una pantalla móvil o tablet
        if (container.classList.contains('toggle')) {
            welcomeSignIn.style.display = 'flex';
            welcomeSignUp.style.display = 'none';
        } else {
            welcomeSignIn.style.display = 'none';
            welcomeSignUp.style.display = 'flex';
        }
    } else { // Para pantallas de escritorio
        welcomeSignIn.style.display = ''; // Restablecer a default CSS
        welcomeSignUp.style.display = ''; // Restablecer a default CSS
    }
}// login modal 

document.getElementById("openModal").onclick = function() {
  document.getElementById("loginModal").style.display = "block";
};

document.querySelector(".close").onclick = function() {
  document.getElementById("loginModal").style.display = "none";
};

window.onclick = function(event) {
  const modal = document.getElementById("loginModal");
  if (event.target === modal) {
    modal.style.display = "none";
  }
};

btnTurnos.onclick = function() {
  modal.style.display = "block";
  opcionesDashboard.style.display = "none"; // ocultar opciones
}

// Cerrar modal
spanClose.onclick = function() {
  modal.style.display = "none";
  opcionesDashboard.style.display = "flex"; // mostrar opciones otra vez
}

// Cerrar modal si se hace click fuera del contenido
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
    opcionesDashboard.style.display = "flex";
  }
}

// Llama a la función al cargar y al redimensionar la ventana
window.addEventListener('load', updateWelcomeVisibility);
window.addEventListener('resize', updateWelcomeVisibility);

// También llama a la función cuando se haga clic en los botones
btnSignUp.addEventListener('click', updateWelcomeVisibility);
btnSignIn.addEventListener('click', updateWelcomeVisibility);