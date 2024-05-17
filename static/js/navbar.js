// Checks if the page is scrolled, and updates the navbar visuals accordingly
window.addEventListener('scroll', function() {
  const nav = document.querySelector('nav');
  const searchForm = document.getElementById('searchForm');
  const viewportHeight = window.innerHeight / 2;

  if (window.innerWidth <= 600 || window.pageYOffset > 0) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }

  if (window.pageYOffset > viewportHeight) {
    searchForm.classList.remove('hide-search'); // Show search bar on scroll
  } else {
    searchForm.classList.add('hide-search'); // Hide search bar when at the top
  }
});