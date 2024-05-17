window.onload = function() {
  document.getElementById('readMore').addEventListener('click', function(event) {
    event.preventDefault();
    window.scrollBy({
      top: window.innerHeight / 1.5,
      left: 0,
      behavior: 'smooth'
    });
  });
};