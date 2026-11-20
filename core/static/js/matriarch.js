(() => {
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('mainNav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    toggle.textContent = opened ? '✕' : '☰';
    toggle.setAttribute('aria-expanded', String(opened));
  });
  document.querySelectorAll('.nav-group > .nav-link').forEach(link => {
    link.addEventListener('click', event => {
      if (window.innerWidth <= 900) {
        event.preventDefault();
        link.parentElement.classList.toggle('open');
      }
    });
  });
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900 && !link.parentElement.classList.contains('nav-group')) {
        nav.classList.remove('open');
        toggle.textContent = '☰';
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  });
})();
