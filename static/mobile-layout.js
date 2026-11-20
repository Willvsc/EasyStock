// Sprint 09: menu acessivel em dispositivos moveis.
(() => {
  const toggle = document.getElementById('menuToggle');
  const overlay = document.getElementById('menuOverlay');
  const sidebar = document.getElementById('menuLateral');
  if (!toggle || !overlay || !sidebar) return;
  const mq = window.matchMedia('(max-width: 800px)');
  const close = () => {
    document.body.classList.remove('mobile-menu-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menu de navegacao');
    overlay.hidden = true;
  };
  const open = () => {
    document.body.classList.add('mobile-menu-open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Fechar menu de navegacao');
    overlay.hidden = false;
    sidebar.querySelector('a, button')?.focus();
  };
  toggle.addEventListener('click', () => document.body.classList.contains('mobile-menu-open') ? close() : open());
  overlay.addEventListener('click', () => { close(); toggle.focus(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.body.classList.contains('mobile-menu-open')) { close(); toggle.focus(); }
  });
  sidebar.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
  mq.addEventListener('change', close);
})();
