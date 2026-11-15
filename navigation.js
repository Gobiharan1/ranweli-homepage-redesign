const menu = document.querySelector('.menu');
const navigation = document.querySelector('#site-nav');
function closeMenu() { menu.setAttribute('aria-expanded', 'false'); }
menu.addEventListener('click', () => menu.setAttribute('aria-expanded', String(menu.getAttribute('aria-expanded') === 'false')));
navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menu.focus();
  }
});
