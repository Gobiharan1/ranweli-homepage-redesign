const enquiry = document.querySelector('[data-enquiry]');

if (enquiry) {
  const isTransfer = enquiry.dataset.enquiry === 'transfer';
  enquiry.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(enquiry);
    const data = name => fields.get(name)?.trim();
    const lines = isTransfer ? [
      'Hello Ranweli Tours! I’d like a transfer quote.',
      'Pickup: ' + data('pickup'),
      'Destination: ' + data('destination'),
      'Pickup date: ' + data('date'),
      'Passengers: ' + data('passengers'),
      'Preferred vehicle: ' + data('vehicle')
    ] : [
      'Hello Ranweli Tours! I’d like to plan a trip.',
      'Name: ' + data('name'),
      'Interested in: ' + data('interest'),
      'Travelers: ' + data('travelers'),
      data('month') && 'Travel month: ' + data('month')
    ];
    const url = new URL(enquiry.action);
    url.searchParams.set('text', [...lines, data('notes')].filter(Boolean).join('\n'));
    window.open(url.href, '_blank', 'noopener,noreferrer');
  });
  enquiry.hidden = false;

  document.querySelectorAll('[data-pickup]').forEach(route => {
    route.addEventListener('click', () => {
      enquiry.elements.pickup.value = route.dataset.pickup;
      enquiry.elements.destination.value = route.dataset.destination;
      enquiry.elements.date.focus();
    });
    route.nextElementSibling.hidden = true;
    route.hidden = false;
  });
}

const revealSections = document.querySelectorAll('.about-page [data-reveal]');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (revealSections.length && 'IntersectionObserver' in window && !prefersReducedMotion.matches) {
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.remove('reveal-pending');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  revealSections.forEach(section => {
    section.classList.add('reveal-pending');
    revealObserver.observe(section);
  });
  prefersReducedMotion.addEventListener('change', event => {
    if (event.matches) {
      revealObserver.disconnect();
      revealSections.forEach(section => section.classList.remove('reveal-pending'));
    }
  });
}
