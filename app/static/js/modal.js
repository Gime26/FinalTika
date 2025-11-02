// Mostrar y ocultar modal
const modal = document.getElementById("loginModal");
const btn = document.getElementById("openModal");
const closeBtn = document.querySelector(".close");

btn.onclick = () => modal.style.display = "flex";
closeBtn.onclick = () => modal.style.display = "none";
window.onclick = (e) => {
  if (e.target === modal) modal.style.display = "none";
};
