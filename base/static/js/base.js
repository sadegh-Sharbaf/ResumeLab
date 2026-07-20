(() => {
  const body = document.body;
  const savedTheme = localStorage.getItem('resumelab-theme');
  if (savedTheme === 'light') body.classList.add('light');

  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    body.classList.toggle('light');
    localStorage.setItem('resumelab-theme', body.classList.contains('light') ? 'light' : 'dark');
  });

  const menu = document.querySelector('[data-main-menu]');
  const toggle = document.querySelector('[data-menu-toggle]');
  toggle?.addEventListener('click', () => {
    const open = menu?.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(Boolean(open)));
  });
  menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => menu.classList.remove('open')));

  setTimeout(() => document.querySelectorAll('.message').forEach(el => el.remove()), 5000);
})();
