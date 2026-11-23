"""Build the checked-in GitHub Pages routes. Run with python3 tools/build_pages.py."""
from dataclasses import dataclass
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://ranwelitours.com/"
WHATSAPP = "https://wa.me/94762566946"
CATEGORIES = {
    "day": "Day trips", "round": "Multi-day tours",
    "ramayana": "Ramayana trails", "east": "East Coast tours",
}
SERIES = {"ramayana": "ramayana-tours-sri-lanka", "east": "east-coast-tours-sri-lanka"}
NAV = (("Tours", "tours/"), ("Special tours", "special-tours/"), ("Transfers", "transfers/"),
       ("About us", "about/"), ("Gallery", "gallery/"))

@dataclass
class Tour:
    category: str
    slug: str
    name: str
    days: int
    image: str
    description: str
    stops: list[str]

    @classmethod
    def parse(cls, row):
        category, slug, name, days, image, description, stops = row.split("|")
        return cls(category, slug, name, int(days), image, description, stops.split("~"))

    @property
    def duration(self):
        return "Day trip" if self.days == 1 else f"{self.days} days · {self.days - 1} nights"

TOURS = [
    Tour.parse(row) for row in (ROOT / "tools/tours.txt").read_text().splitlines()
    if row and not row.startswith("#")
]


def button(label, url, style="dark"):
    return f'<a class="button {style}" href="{escape(url, quote=True)}">{escape(label)} <span aria-hidden="true">↗</span></a>'


def whatsapp(message):
    return f"{WHATSAPP}?text={quote(message)}"


def source_link(slug="", label="See the original Ranweli Tours page"):
    return f'<a class="text-link" href="{SOURCE}{slug.rstrip("/") + "/" if slug else ""}">{escape(label)} ↗</a>'


def hero(title, description, photo, breadcrumb, action="", position="center"):
    return f"""
<section class="page-hero" aria-labelledby="page-title" style="--image-position:{position}">
  <img src="{{root}}assets/{photo}.webp" alt="" fetchpriority="high">
  <div class="wrap page-hero-content">
    <div class="breadcrumbs">{breadcrumb}</div>
    <h1 id="page-title">{title}</h1>
    <p>{escape(description)}</p>{action}
  </div>
</section>"""


def write_page(path, title, description, contents, active=""):
    prefix = "../" * len(Path(path).parts)
    nav = "".join(
        f'<a href="{prefix}{link}"' + (' aria-current="page"' if link == active else "") + f'>{label}</a>'
        for label, link in NAV
    )
    logo = f'<a class="brand" href="{prefix}"><img src="{prefix}assets/ranweli-logo.png" alt="Ranweli Tours home" width="300" height="150"></a>'
    footer_links = "".join(
        f'<a href="{prefix}{url}">{label}</a>' for label, url in (
            ("Tours", "tours/"), ("Transfers", "transfers/"), ("Travel guides", "travel-guides/"),
            ("Contact", "contact/"),
        )
    )
    policies = "".join(
        f'<a href="{SOURCE}{url}/">{label} ↗</a>' for label, url in (
            ("Privacy", "privacy-policy"), ("Terms", "terms-and-conditions"),
            ("Refunds and cancellations", "refund-cancellation-policy"),
        )
    )
    out = ROOT / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}">
<title>{escape(title)} | Ranweli Tours</title>
<link rel="stylesheet" href="{prefix}style.css">
<link rel="stylesheet" href="{prefix}pages.css">
<script src="{prefix}navigation.js" defer></script>
<script src="{prefix}pages.js" defer></script>
</head>
<body class="inner-page">
<a class="skip" href="#main">Skip to content</a>
<header class="header">
  <div class="wrap bar">
    {logo}
    <button class="menu" type="button" aria-expanded="false" aria-controls="site-nav">Menu <span aria-hidden="true">☰</span></button>
    <nav id="site-nav" aria-label="Main navigation">{nav}</nav>
    {button("Plan my trip", prefix + "contact/", "header-cta")}
  </div>
</header>
<main id="main">{contents.replace("{root}", prefix)}
</main>
<footer>
  <div class="wrap footer-row">
    {logo}
    <div>{footer_links}</div>
    <small>© Ranweli Tours</small>
  </div>
  <div class="wrap policies">{policies}</div>
</footer>
</body>
</html>
""", encoding="utf-8")


def tour_card(tour):
    return f"""
<article class="package-card">
  <a class="package-photo" href="{{root}}tours/{tour.slug}/" aria-label="{escape(tour.name)}">
    <img src="{{root}}assets/{tour.image}.webp" alt="" loading="lazy">
    <span class="duration">{tour.duration}</span>
  </a>
  <div class="package-copy">
    <h3>{escape(tour.name)}</h3>
    <p>{escape(tour.description)}</p>
    <a class="package-link" href="{{root}}tours/{tour.slug}/" aria-label="Explore {escape(tour.name)}">View itinerary <span aria-hidden="true">↗</span></a>
  </div>
</article>"""


def tour_groups(categories):
    links = "".join(f'<a class="button" href="#{key}">{CATEGORIES[key]}</a>' for key in categories)
    groups = []
    for key in categories:
        cards = "".join(tour_card(tour) for tour in TOURS if tour.category == key)
        groups.append(f'<section class="section catalog-group" id="{key}"><div class="wrap">'
                      f'<h2>{CATEGORIES[key]}</h2><div class="package-grid">{cards}</div></div></section>')
    return f'<div class="wrap category-links" aria-label="Jump to tour type">{links}</div>' + "".join(groups)


def callout(title, copy, label, href):
    return f"""<section class="section page-callout">
  <div class="wrap">
    <div><h2>{title}</h2><p>{escape(copy)}</p></div>
    {button(label, href, "gold")}
  </div>
</section>"""


def home_breadcrumb(label):
    return f'<a href="{{root}}">Home</a> <span aria-hidden="true">/</span> {escape(label)}'


def field(label, name, kind="text", options=(), full=False, required=True):
    class_attr = ' class="full"' if full else ""
    required_attr = " required" if required else ""
    if options:
        choices = "".join(f"<option>{escape(value)}</option>" for value in options)
        control = f'<select name="{name}"{required_attr}>{choices}</select>'
    elif kind == "textarea":
        control = f'<textarea name="{name}" rows="3" maxlength="500"{required_attr}></textarea>'
    else:
        attributes = {
            "number": ' min="1" max="999" inputmode="numeric"',
            "text": ' maxlength="120"' + (' autocomplete="name"' if name == "name" else ""),
        }
        control = f'<input type="{kind}" name="{name}"{attributes.get(kind, "")}{required_attr}>'
    return f"<label{class_attr}>{label}{control}</label>"


def enquiry_form(kind, fields):
    return f"""
<form class="page-form" data-enquiry="{kind}" hidden action="{WHATSAPP}" target="_blank" rel="noopener noreferrer">
  {''.join(fields)}
  <button class="button gold full" type="submit">Continue to WhatsApp <span aria-hidden="true">↗</span></button>
  <small class="full form-note">Review the message in WhatsApp before sending it to Ranweli Tours.</small>
</form>
<noscript><p>{button("Open WhatsApp", WHATSAPP, "gold")}</p></noscript>"""


def build_catalogue():
    description = "Compare private Sri Lanka tours by duration and travel style, from a day in Kandy to a two-week island circuit."
    write_page("tours", "Sri Lanka tour packages", description,
               hero("Find your <em>Sri Lanka tour</em>", description, "highlands", home_breadcrumb("Tours"),
                    button("Browse the tours", "#catalogue", "light"), "center 57%")
               + '<div id="catalogue">' + tour_groups(CATEGORIES) + "</div>"
               + callout("Make it <em>your own</em>", "Tell us how long you have and what you’d like to see.",
                         "Plan a custom trip", "{root}contact/"), "tours/")

    description = "Choose a Ramayana pilgrimage through sacred sites or a private journey along Sri Lanka’s east coast."
    features = "".join(
        f'<a class="series-card" href="{{root}}tours/{SERIES[key]}/"><img src="{{root}}assets/{asset}.webp" alt="">'
        f'<div><h3>{CATEGORIES[key]}</h3><p>{copy}</p><span aria-hidden="true">↗</span></div></a>'
        for key, asset, copy in (
            ("ramayana", "kovil", "Temples, pilgrimage sites and the traditions that connect them."),
            ("east", "coast", "Trincomalee, Pigeon Island, Pasikudah and Arugam Bay."),
        )
    )
    write_page("special-tours", "Special tours", description,
               hero("Follow a <em>different route</em>", description, "hero-3499", home_breadcrumb("Special tours"),
                    position="center 48%")
               + f'<section class="section wrap"><h2>Choose your <em>journey</em></h2><div class="series-grid">{features}</div></section>',
               "special-tours/")

    for category, (title, copy, image) in {
        "ramayana": ("Follow the <em>Ramayana trail</em>",
                     "Explore temples and landscapes associated with the Ramayana tradition, from Chilaw and Kandy to the hill country and the south.",
                     "kovil"),
        "east": ("Explore the <em>east coast</em>",
                 "Choose between coastal stays and longer journeys linking beaches, marine excursions, wildlife and ancient cities.",
                 "coast"),
    }.items():
        write_page(f"tours/{SERIES[category]}", CATEGORIES[category], copy,
                   hero(title, copy, image, home_breadcrumb(CATEGORIES[category]))
                   + tour_groups([category])
                   + f'<div class="wrap page-source">{source_link(SERIES[category])}</div>', "special-tours/")

    for tour in TOURS:
        assert tour.days == 1 or len(tour.stops) == tour.days, tour.slug
        crumb_url = f"{{root}}tours/{SERIES[tour.category]}/" if tour.category in SERIES else f"{{root}}tours/#{tour.category}"
        crumb = f'<a href="{crumb_url}">{CATEGORIES[tour.category]}</a> <span aria-hidden="true">/</span> {tour.duration}'
        url = whatsapp(f"Hello Ranweli Tours, I’d like to ask about {tour.name}. Could you share availability and a quote?")
        stops = "".join(
            f'<li><span>{"Stop" if tour.days == 1 else "Day"} {num:02}</span><p>{escape(stop)}</p></li>'
            for num, stop in enumerate(tour.stops, 1)
        )
        related = [item for item in TOURS if item.category == tour.category and item.slug != tour.slug]
        related.sort(key=lambda item: abs(item.days - tour.days))
        write_page(f"tours/{tour.slug}", tour.name, tour.description,
                   hero(escape(tour.name), tour.description, tour.image, crumb, button("Enquire on WhatsApp", url, "light"))
                   + f"""
<section class="wrap section trip-layout">
  <div><h2>{'Tour <em>highlights</em>' if tour.days == 1 else 'Your <em>itinerary</em>'}</h2>
    <ol class="itinerary">{stops}</ol>
    {source_link(tour.slug, "Read the original full itinerary")}
  </div>
  <aside class="quote-card">
    <p class="quote-duration">{tour.duration}</p><h3>Ask about this tour</h3>
    <p>Share your dates and group size. The Ranweli team can confirm pickup, pricing and what’s included.</p>
    {button("Ask for a quote", url, "gold")}
    <a class="text-link" href="{{root}}transfers/">Need a separate transfer? ↗</a>
  </aside>
</section>
<section class="section catalog-group related"><div class="wrap">
  <h2>More <em>{CATEGORIES[tour.category].lower()}</em></h2>
  <div class="package-grid">{''.join(tour_card(item) for item in related[:3])}</div>
</div></section>""", "special-tours/" if tour.category in SERIES else "tours/")


def build_transfers():
    routes = (
        ("Colombo Airport", "Kandy", 54), ("Colombo Airport", "Nuwara Eliya", 78),
        ("Colombo Airport", "Galle / Unawatuna", 56), ("Kandy", "Sigiriya / Dambulla", 42),
        ("Kandy", "Nuwara Eliya", 52), ("Nuwara Eliya", "Ella", 40),
        ("Ella", "Yala National Park", 46), ("Galle", "Mirissa / Matara", 26),
        ("Negombo", "Colombo City", 20), ("Anuradhapura", "Polonnaruwa", 60),
    )
    route_cards = "".join(f"""
<li><button type="button" data-pickup="{pickup}" data-destination="{destination}" hidden>
  <span>{pickup} <span aria-hidden="true">→</span> {destination}</span><strong>From US${fare}</strong>
</button><span class="route-static">{pickup} → {destination} <strong>From US${fare}</strong></span></li>"""
        for pickup, destination, fare in routes)
    description = "Arrange a private airport pickup, hotel transfer or city-to-city ride with a local driver."
    form = enquiry_form("transfer", [
        field("Pickup location", "pickup"), field("Destination", "destination"),
        field("Pickup date", "date", "date"), field("Passengers", "passengers", "number"),
        field("Preferred vehicle", "vehicle", options=("Recommend a vehicle", "Car", "SUV", "Van", "Bus"), full=True, required=False),
        field("Flight number, pickup time or luggage (optional)", "notes", "textarea", full=True, required=False),
    ])
    write_page("transfers", "Private transfers in Sri Lanka", description,
               hero("Private transfers <em>across Sri Lanka</em>", description, "transport", home_breadcrumb("Transfers"),
                    button("Request a transfer", "#quote", "light"), "center 54%")
               + f"""
<section class="section wrap">
  <div class="section-intro"><h2>Popular <em>transfer routes</em></h2>
  <p>Published starting prices in US dollars for a private car carrying 1–3 passengers. Ask for a quote for your date, a larger group or another route.</p></div>
  <ul class="route-list">{route_cards}</ul>
  {source_link("transfer", "See the original transfer rates")}
</section>
<section class="plan section" id="quote">
  <div class="wrap plan-grid">
    <div><h2>Tell us where <em>you’re going</em></h2>
      <p>Ranweli arranges air-conditioned vehicles and English-speaking drivers. For same-day pickup, contact the team directly to check availability.</p>
      <a class="text-link" href="tel:+94762566946">+94 76 256 6946</a>
    </div>
{form.strip()}
  </div>
</section>""", "transfers/")


def build_company_pages():
    description = "Meet the Sri Lanka team behind Ranweli Tours and see how they plan private journeys around the island."
    about_photos = (
        ("hero-3521", "A hill-country walk with Ranweli Tours"),
        ("hero-3499", "Travelers visiting a temple in Matale"),
        ("group", "A group exploring Sri Lanka with their local guide"),
        ("coconuts", "A roadside stop for king coconuts"),
        ("hero-4234", "Travelers on a forest visit"),
    )
    photo_strip = "".join(
        f'<figure><img src="{{root}}assets/{photo}.webp" alt="{caption}" loading="lazy"></figure>'
        for photo, caption in about_photos
    )
    values = (
        ("A journey shaped around you",
         "Start with the places you’re curious about. We’ll help connect them into a route that suits your dates, group and pace, whether you have a day in Kandy or two weeks to explore the island.",
         "hero-3521", "A traveler and guide in Sri Lanka’s hill country", "Explore our tours", "tours/"),
        ("Local people, closer connections",
         "Our Sri Lankan team works with local businesses and communities along the way. From temple visits to a shared meal, these are opportunities to spend time with the people who know each place.",
         "local-lunch", "A Sri Lankan meal shared outdoors", "See our travel moments", "gallery/"),
        ("Support from pickup to your last stop",
         "Talk to our team about airport pickups, private transfers and the days in between. We’ll help arrange a suitable vehicle and discuss your route and travel details before you set off.",
         "transport", "Travelers beside a Ranweli Tours vehicle", "Arrange a transfer", "transfers/"),
    )
    value_rows = "".join(
        f'<details class="about-value" name="ranweli-values"{" open" if index == 0 else ""}>'
        f'<summary><h3>{title}</h3><span class="value-toggle" aria-hidden="true"></span></summary>'
        f'<div class="value-content"><div><p>{copy}</p><a class="text-link" href="{{root}}{url}">{label}</a></div>'
        f'<img src="{{root}}assets/{photo}.webp" alt="{alt}" loading="lazy"></div></details>'
        for index, (title, copy, photo, alt, label, url) in enumerate(values)
    )
    write_page("about", "About Ranweli Tours", description,
               '<div class="about-page">'
               + hero("See Sri Lanka <em>with locals</em>",
                      "Private journeys. Local connections. Memories from the road.",
                      "hero-3521", home_breadcrumb("About us"),
                      button("Get to know us", "#our-story", "light"), "center 38%")
               + f"""
<section class="about-intro section" id="our-story" aria-labelledby="about-statement">
  <div class="wrap centered about-statement" data-reveal>
    <p class="about-eyebrow">ABOUT RANWELI</p>
    <h2 id="about-statement">Every journey has a route.<br><em>Yours should have a story.</em></h2>
    <p>Ancient cities, mountain mornings and the people you meet along the way. Discover Sri Lanka at your own pace, with a local team by your side.</p>
  </div>
  <div class="about-photo-strip" aria-label="Journeys with Ranweli Tours" data-reveal>{photo_strip}</div>
  <div class="wrap about-story" data-reveal>
    <p class="about-eyebrow">OUR STORY</p>
    <div><h2>A local team.<br><em>A personal way to travel.</em></h2>
      <p>Founded by Nilanka Lakmal, Ranweli Tours is a Sri Lankan team that helps travelers plan private trips around the island. The team works with local businesses and communities to arrange visits and experiences along each route.</p>
      <p>Start with a published itinerary or tell the team what interests you. They can shape your travel days around temples, tea country, wildlife and the coast, and arrange a suitable vehicle for your group.</p>
    </div>
  </div>
</section>
<section class="about-values section" aria-labelledby="about-values-title">
  <div class="wrap">
    <div class="centered about-values-heading" data-reveal>
      <p class="about-eyebrow">TRAVEL WITH RANWELI</p>
      <h2 id="about-values-title">The details that make<br><em>the journey yours.</em></h2>
    </div>
    <div class="about-value-list" data-reveal>{value_rows}</div>
  </div>
</section>
<section class="about-finale section">
  <div class="wrap centered" data-reveal>
    <p class="about-eyebrow">YOUR NEXT CHAPTER</p>
    <h2>Where would you<br><em>like to go?</em></h2>
    <p>Bring your ideas. We’ll help you find the route.</p>
    {button("Let’s plan your trip", "{root}contact/", "gold")}
  </div>
</section>
</div>""", "about/")

    gallery = (
        ("hero-3521", "A day in the hill country"), ("hero-3499", "The Hindu temple in Matale"),
        ("hero-1152", "Travellers at Sigiriya Museum"), ("hero-2135", "A visit to an ancient stupa"),
        ("hero-4234", "A group visit in the forest"), ("group", "Exploring the ancient cities"),
        ("coconuts", "A stop for king coconuts"), ("tea", "Tea picking in the hills"),
        ("transport", "Guests beside a Ranweli Tours van"), ("local-lunch", "A Sri Lankan meal outdoors"),
        ("waterfall", "Stopping at a waterfall"), ("coast", "Time on Sri Lanka’s coast"),
    )
    gallery_tiles = "".join(
        f'<figure><a href="{{root}}assets/{asset}.webp"><img src="{{root}}assets/{asset}.webp" alt="{escape(caption)}" loading="lazy">'
        f'</a><figcaption>{escape(caption)}</figcaption></figure>' for asset, caption in gallery
    )
    description = "Photos from journeys with Ranweli Tours, from tea country and temple visits to coast and roadside stops."
    write_page("gallery", "Photo gallery", description,
               hero("Moments <em>from the road</em>", description, "hero-4234", home_breadcrumb("Gallery"),
                    position="center 60%")
               + f'<section class="section wrap"><h2>Out and about <em>with Ranweli</em></h2><div class="photo-wall">{gallery_tiles}</div></section>',
               "gallery/")

    description = "Talk to the Ranweli team about a tour, a private transfer or a Sri Lanka itinerary built around your dates."
    form = enquiry_form("trip", [
        field("Your name", "name"), field("Travel month (optional)", "month", "month", required=False),
        field("Number of travelers", "travelers", "number"),
        field("I’m interested in", "interest", options=("A custom Sri Lanka trip", "Day trips", "Multi-day tours",
                                                       "Ramayana trails", "East Coast tours", "A private transfer")),
        field("Anything else? (optional)", "notes", "textarea", full=True, required=False),
    ])
    write_page("contact", "Contact Ranweli Tours", description,
               hero("Let’s plan <em>your Sri Lanka</em>", description, "local-lunch", home_breadcrumb("Contact"),
                    button("Send an enquiry", "#enquiry", "light"))
               + f"""
<section class="plan section" id="enquiry"><div class="wrap plan-grid">
  <div><h2>Talk to <em>our team</em></h2>
    <p>Tell us where you want to go, how many are travelling and when you’ll be here. We can help you decide on a route or confirm a tour you’ve chosen.</p>
    <ul class="contact-links">
      <li><a class="text-link" href="tel:+94762566946">Call +94 76 256 6946</a></li>
      <li><a class="text-link" href="{WHATSAPP}">Chat on WhatsApp ↗</a></li>
      <li><a class="text-link" href="mailto:ranwelitour@gmail.com">ranwelitour@gmail.com ↗</a></li>
    </ul>
  </div>
{form.strip()}
</div></section>
""")

    guides = (
        ("East Coast beaches", "Compare the beaches around Trincomalee, Pasikudah and Arugam Bay.", "coast",
         "2026/07/24/best-beaches-on-sri-lankas-east-coast"),
        ("Places to visit on the East Coast", "Explore ideas for temple visits, lagoons and coastal towns.", "kovil",
         "2026/07/24/popular-places-to-visit-on-sri-lankas-east-coast"),
        ("Why visit the East Coast?", "Get a feel for the region’s coastline, marine activities and culture.", "coast",
         "2026/07/24/why-visit-sri-lankas-east-coast"),
        ("Sri Lanka’s waterfalls", "Look for waterfall stops to add to your route through the hills.", "waterfall",
         "2026/03/16/waterfalls-in-sri-lanka"),
        ("A day in Colombo", "Explore ideas for sightseeing in Sri Lanka’s commercial capital.", "market",
         "2026/03/20/colombo-city-tour-the-ultimate-guide-to-exploring-sri-lankas-vibrant-capital"),
        ("Visiting Galle", "Plan time in Galle Fort and on the surrounding coastline.", "coast",
         "2026/03/20/galle-tour-the-ultimate-guide-to-a-perfect-trip-to-galle-in-sri-lanka"),
        ("Tea factories in Nuwara Eliya", "Find out what to expect on an estate and factory visit.", "tea",
         "2026/03/20/nuwara-eliya-tea-factory-tour-experience-the-heart-of-sri-lankas-tea-country"),
        ("Sacred Ramayana sites", "Find places associated with the epic in Sri Lanka.", "kovil",
         "2026/03/20/ramayana-tour-sri-lanka-explore-the-sacred-ramayana-places-in-sri-lanka"),
        ("The Ramayana Trail", "Explore the route linking places associated with the Ramayana.", "dambulla",
         "2026/06/11/ramayana-trail-in-sri-lanka"),
        ("What is the Ramayana?", "Read an introduction to the epic and its place in the pilgrimage tradition.", "hero-3499",
         "2026/06/13/what-is-ramayana"),
    )
    guide_cards = "".join(
        f'<article class="package-card"><div class="package-photo"><img src="{{root}}assets/{image}.webp" alt="" loading="lazy"></div>'
        f'<div class="package-copy"><h3>{title}</h3><p>{copy}</p>'
        f'<a class="package-link" href="{SOURCE}{slug}/" aria-label="Read {title}">Read the guide <span aria-hidden="true">↗</span></a></div></article>'
        for title, copy, image, slug in guides
    )
    description = "Plan your Sri Lanka journey with destination guides from Ranweli Tours."
    write_page("travel-guides", "Sri Lanka travel guides", description,
               hero("Notes <em>from Sri Lanka</em>", description, "coast", home_breadcrumb("Travel guides"))
               + f'<section class="section wrap"><h2>Ideas for <em>your journey</em></h2><div class="package-grid">{guide_cards}</div>'
               + f'<p>{source_link("blog", "Browse the original Ranweli travel blog")}</p></section>')


if __name__ == "__main__":
    build_catalogue()
    build_transfers()
    build_company_pages()
