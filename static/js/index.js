window.onload = function() {
  document.getElementById('readMore').addEventListener('click', function(event) {
    event.preventDefault();
    window.scrollBy({
      top: window.innerHeight,
      left: 0,
      behavior: 'smooth'
    });
  });
};