// Checks if the page is scrolled, and updates the navbar visuals accordingly
window.addEventListener('scroll', function() {
  const nav = document.querySelector('nav');
  if (window.pageYOffset > 0) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }
});