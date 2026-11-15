const base = 'tours/';
const tours = [
  ['round', 'Sri Lanka in 8 Days', '8 days · 7 nights', 'Explore ancient cities, climb Sigiriya and head into the island’s tea country.', 'highlands', 'Travelers by the Nine Arch Bridge railway in Ella', 'sri-lanka-8-day-tour-7-nights/'],
  ['round', 'Sri Lanka in 4 Days', '4 days · 3 nights', 'A short island circuit with time for history, temples and lush inland scenery.', 'heritage', 'Travelers visiting the ruins of Polonnaruwa', 'sri-lanka-4-day-tour-package/'],
  ['special', 'Ramayana Trails', 'Special interest', 'Visit sacred sites linked to the Ramayana with a route tailored to your group.', 'kovil', 'Ornately decorated Hindu temple in Matale', 'ramayana-tours-sri-lanka/'],
  ['round', 'Sri Lanka in 6 Days', '6 days · 5 nights', 'Explore more of Sri Lanka on a private island journey with your own chauffeur guide.', 'safari', 'Jeep safari across wide grasslands', 'sri-lanka-6-day-tour-package/'],
  ['round', 'Sri Lanka in 13 Days', '13 days · 12 nights', 'Take the longer route through striking landscapes, historic landmarks and coastal towns.', 'coast', 'Travelers by the coast', 'sri-lanka-13-days-tour-12-nights/'],
  ['day', 'Kandy City Tour', 'Full day', 'Visit the Temple of the Sacred Tooth Relic, the botanical gardens and Kandy Lake.', 'kandy', 'Travelers at a temple in Kandy', 'kandy-city-tour/'],
  ['day', 'Nuwara Eliya from Kandy', 'Day trip', 'Spend a day among tea estates and cool highland scenery on the way to Nuwara Eliya.', 'tea', 'Picking leaves at a tea plantation', 'kandy-to-nuwara-eliya-city-tour/'],
  ['day', 'Ella Day Tour', 'Day trip', 'Explore Ella and its hill-country views, waterfalls and railway landmarks.', 'highlands', 'Travelers by the Nine Arch Bridge railway in Ella', 'ella-city-tour/'],
  ['special', 'East Coast Tours', 'Special interest', 'Shape a coastal break around destinations like Trincomalee and Pasikudah.', 'coast', 'Travelers on a beach in Sri Lanka', 'east-coast-tours-sri-lanka/']
];
const photos = [
  ['group', 'A Ranweli group exploring the ancient cities'],
  ['dambulla', 'The Golden Temple in Dambulla'],
  ['coconuts', 'A roadside stop for king coconuts'],
  ['local-lunch', 'A Sri Lankan lunch shared outdoors'],
  ['waterfall', 'A waterfall stop with a Ranweli guide'],
  ['transport', 'Guests beside a Ranweli Tours van'],
  ['market', 'An evening in a local market'],
  ['tea', 'Tea picking in the hill country']
];
const interests = [
  'A custom Sri Lanka trip', 'Airport pickup or private transfer', 'Ancient sites and temples',
  'Tea country and scenic trains', 'Wildlife and jeep safaris', 'Beaches and coastal towns',
  ...tours.map(([, name]) => name)
];
const interest = document.querySelector('#interest');
interest.replaceChildren(...interests.map(name => new Option(name, name)));

const grid = document.querySelector('#tour-grid');
const filters = [...document.querySelectorAll('[data-filter]')];
const featuredTours = [tours[1], tours[2], tours[0], tours[3], tours[4]];
const tourPrevious = document.querySelector('#tour-prev');
const tourNext = document.querySelector('#tour-next');
const tourStatus = document.querySelector('#tour-status');
let tourCategory = 'all';
let activeTour = 2;

function showTours() {
  const options = tourCategory === 'all' ? featuredTours : tours.filter(([type]) => type === tourCategory);
  const count = options.length;
  const middle = Math.floor(count / 2);
  const selected = options[activeTour];
  const visible = options.map((_, i) => options[(i + activeTour - middle + count) % count]);
  grid.innerHTML = visible.map((tour, i) => {
    const [, name, duration, copy, asset, alt, path] = tour;
    return `
      <article class="tour" data-distance="${Math.abs(i - middle)}">
        <img loading="lazy" src="assets/${asset}.webp" alt="${alt}">
        <div class="tour-copy"><span class="duration">${duration}</span><h3>${name}</h3><p>${copy}</p>
        <a class="button light" href="${base}${path}" aria-label="Explore ${name}">Explore <span aria-hidden="true">↗</span></a></div>
      </article>`;
  }).join('');
  filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === tourCategory)));
  tourStatus.textContent = `${count} tours shown. ${selected[1]} is centered.`;
  const centered = grid.children[middle];
  grid.scrollLeft = centered.offsetLeft + centered.offsetWidth / 2 - grid.clientWidth / 2;
}
function changeTour(offset) {
  const count = grid.children.length;
  activeTour = (activeTour + offset + count) % count;
  showTours();
}
filters.forEach(button => button.addEventListener('click', () => {
  tourCategory = button.dataset.filter;
  activeTour = tourCategory === 'all' ? 2 : 0;
  showTours();
}));
tourPrevious.addEventListener('click', () => changeTour(-1));
tourNext.addEventListener('click', () => changeTour(1));
showTours();
document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => {
  interest.value = link.dataset.interest;
}));

const dialog = document.querySelector('#lightbox');
const dialogImage = dialog.querySelector('img');
const caption = dialog.querySelector('figcaption');
let current = 0;
function displayPhoto(index) {
  current = (index + photos.length) % photos.length;
  const [asset, description] = photos[current];
  dialogImage.src = `assets/${asset}.webp`;
  dialogImage.alt = description;
  caption.textContent = `${description} · ${current + 1} / ${photos.length}`;
}
const gallery = document.querySelector('#photos');
function openGallery(index) {
  displayPhoto(index);
  dialog.showModal();
}
photos.slice(0, 5).forEach(([asset, description], index) => {
  const button = document.createElement('button');
  button.type = 'button';
  button.setAttribute('aria-label', `View photo: ${description}`);
  button.innerHTML = `<img loading="lazy" src="assets/${asset}.webp" alt=""><span aria-hidden="true">↗</span>`;
  button.addEventListener('click', () => openGallery(index));
  gallery.append(button);
});
document.querySelector('#all-photos').addEventListener('click', () => openGallery(0));
dialog.querySelector('.close').addEventListener('click', () => dialog.close());
dialog.querySelector('.next').addEventListener('click', () => displayPhoto(current + 1));
dialog.querySelector('.prev').addEventListener('click', () => displayPhoto(current - 1));
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
dialog.addEventListener('keydown', event => {
  if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
  event.preventDefault();
  displayPhoto(current + (event.key === 'ArrowRight' ? 1 : -1));
});
document.querySelector('#enquiry').addEventListener('submit', event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const month = form.get('month');
  const message = [
    'Hello Ranweli Tours! I’d like to plan a trip.',
    `Name: ${form.get('name').trim()}`,
    `Interested in: ${form.get('interest')}`,
    `Travelers: ${form.get('travelers')}`,
    month && `Travel month: ${month}`,
    form.get('notes').trim()
  ].filter(Boolean).join('\n');
  window.open(`https://wa.me/94762566946?text=${encodeURIComponent(message)}`, '_blank', 'noopener,noreferrer');
});

const heroPhotos = document.querySelector('.hero-photos');
const photoButtons = [...document.querySelectorAll('.hero-controls [data-photo]')];
const heroCaption = document.querySelector('#hero-caption');
const heroPlay = document.querySelector('.hero-play');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const photoInterval = 4000;
let heroIndex = 0;
let playing = !reducedMotion.matches;
let heroTimer;
let loadingPhoto;

function scheduleHero() {
  clearTimeout(heroTimer);
  heroPlay.textContent = playing ? 'Pause' : 'Play';
  heroPlay.setAttribute('aria-label', playing ? 'Pause photo slideshow' : 'Play photo slideshow');
  if (playing && !document.hidden) {
    heroTimer = setTimeout(() => showHeroPhoto((heroIndex + 1) % photoButtons.length, true), photoInterval);
  }
}

async function showHeroPhoto(index, automatic = false) {
  clearTimeout(heroTimer);
  loadingPhoto = undefined;
  if (index === heroIndex) {
    scheduleHero();
    return;
  }

  const { photo, caption: label, position } = photoButtons[index].dataset;
  const incoming = new Image();
  loadingPhoto = incoming;
  incoming.className = 'hero-img';
  incoming.alt = '';
  incoming.style.setProperty('--photo-position', position);
  incoming.src = `assets/${photo}.webp`;

  try {
    await incoming.decode();
  } catch {
    if (loadingPhoto === incoming) scheduleHero();
    return;
  }
  if (loadingPhoto !== incoming || (automatic && (!playing || document.hidden))) return;

  const outgoing = heroPhotos.lastElementChild;
  heroPhotos.append(incoming);
  if (reducedMotion.matches) {
    outgoing.remove();
  } else {
    incoming.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 750, easing: 'ease-in-out' })
      .finished.then(() => outgoing.remove(), () => outgoing.remove());
  }
  heroIndex = index;
  heroCaption.textContent = label;
  photoButtons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
  scheduleHero();
}

photoButtons.forEach((button, index) => button.addEventListener('click', () => {
  playing = false;
  scheduleHero();
  showHeroPhoto(index);
}));
heroPlay.addEventListener('click', () => {
  playing = !playing;
  scheduleHero();
});
reducedMotion.addEventListener('change', event => {
  playing = !event.matches;
  scheduleHero();
});
document.addEventListener('visibilitychange', scheduleHero);
document.querySelector('.hero-gallery').hidden = false;
scheduleHero();
