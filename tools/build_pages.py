"""Builds the site's HTML pages from the catalogue data.

The site is plain static files; this script only regenerates them. Edit the page
templates or the data below, then run from the repository root:

    python3 tools/build_pages.py

Data: tools/works.json (title, size, price, sold, image size for each painting) and
tools/imgs.json (the WebP widths generated for each image).
"""
import json, html, os, re, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + "/"
META = json.load(open(os.path.join(os.path.dirname(__file__), "works.json")))
e = lambda s: html.escape(s, quote=True)
IG = "https://www.instagram.com/akandejjohn/"
# Enquiries and print requests open an email to this address.
EMAIL = "johnakande23@gmail.com"
BANK_ACCOUNTS = [
    ("Naira account", "NGN", [("Account number", "1845785745"), ("Account name", "JOHN TOBI AKANDE"),
                              ("Account type", "Premier Savings"), ("Bank", "Access Bank Nigeria")]),
    ("Domiciliary account", "Foreign currency", [("Account number", "1846380972"), ("Account name", "JOHN TOBI AKANDE"),
                                                 ("Account type", "Dom Savings Classic"), ("Bank", "Access Bank Nigeria"),
                                                 ("SWIFT code", "ABNGNGLA")]),
]
TH = "https://www.threads.net/@akandejjohn"
SITE = "https://johnakande.studio"
IMGS = json.load(open(os.path.join(os.path.dirname(__file__), "imgs.json")))
TODAY = datetime.date.today().isoformat()

def img_base(slug):
    return "assets/img/john-akande" if slug == "john-akande" else f"assets/img/works/{slug}"

def big(slug):
    """Largest WebP, used by the artwork viewer."""
    return f"{img_base(slug)}-{IMGS[slug]['ws'][-1]}.webp"

def mid(slug):
    ws = IMGS[slug]["ws"]
    return f"{img_base(slug)}-{800 if 800 in ws else ws[-1]}.webp"

def pic(slug, alt, sizes, cls="", lazy=True, attrs=""):
    """<img> with WebP srcset at several widths and the JPEG as fallback."""
    m = IMGS[slug]
    srcset = ", ".join(f"{img_base(slug)}-{W}.webp {W}w" for W in m["ws"])
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{img_base(slug)}.jpg" srcset="{srcset}" sizes="{sizes}" alt="{alt}" '
            f'width="{m["w"]}" height="{m["h"]}"{' loading="lazy"' if lazy else ''} decoding="async"{attrs} />')

def page_slug(slug):
    return "rhythm-of-our-heritage" if slug == "rhythm-of-our-heritage-studio" else slug

def clean(url):
    """Drop ".html" from page links (the host serves /works/x from works/x.html); /index becomes /."""
    url = re.sub(r"\.html(?=$|[?#])", "", url)
    return re.sub(r"(^|/)index(?=$|[?#])", r"\1", url)

def absolutize(doc):
    """Root-relative, clean URLs, so pages in /works/ resolve assets and links the same way."""
    def fix(url):
        if re.match(r"^(https?:|mailto:|tel:|data:|#)", url) or not url:
            return url
        return clean(url if url.startswith("/") else "/" + url)
    doc = re.sub(r'\b(href|src|data-src|poster)="([^"]*)"', lambda m: f'{m.group(1)}="{fix(m.group(2))}"', doc)
    doc = re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        fix(p.strip().split(" ")[0]) + (" " + p.strip().split(" ", 1)[1] if " " in p.strip() else "")
        for p in m.group(1).split(",")) + '"', doc)
    # absolute links to this site (canonical, share and structured data) use clean URLs too
    doc = re.sub(re.escape(SITE) + r'(/[^"\s<]*)', lambda m: SITE + clean(m.group(1)), doc)
    # make the email address harder for spam bots to harvest: write it as HTML character codes
    if EMAIL:
        doc = doc.replace(EMAIL, "".join(f"&#{ord(c)};" for c in EMAIL))
    return doc

def currency_switch(compact=False):
    return f"""        <div class="currency{' currency--compact' if compact else ''}">
          <span class="mono currency__label" id="currency-label">Prices in</span>
          <div class="currency__switch" role="group" aria-labelledby="currency-label" data-currency-switch>
            <button type="button" aria-pressed="true" data-currency="USD"><b>$</b> USD</button>
            <button type="button" aria-pressed="false" data-currency="EUR"><b>&euro;</b> EUR</button>
            <button type="button" aria-pressed="false" data-currency="GBP"><b>&pound;</b> GBP</button>
            <button type="button" aria-pressed="false" data-currency="NGN"><b>&#8358;</b> NGN</button>
          </div>
          <p class="mono currency__note" data-currency-note aria-live="polite">Prices are set in US dollars.</p>
        </div>"""

PERSON_LD = {
    "@context": "https://schema.org", "@type": "Person", "name": "John Akande",
    "jobTitle": "Figurative artist", "birthPlace": "Lagos, Nigeria",
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Yaba College of Technology"},
    "url": SITE + "/", "image": SITE + "/assets/img/john-akande.jpg", "sameAs": [IG, TH],
}

STATEMENT = (
    "This body of work explores music as a living force, embedded in human existence. In it, I investigate how "
    "<b>rhythm shapes identity</b>, how <b>performance reveals vulnerability</b>, and how music functions as "
    "<b>cultural memory and therapy</b>."
)
STATEMENT_2 = (
    "It contributes to contemporary African art discourse by positioning music not only as a subject matter but also "
    "as a conceptual framework, highlighting performance as vulnerability and sound as a cultural continuity."
)

PAGES = [("about.html", "About"), ("works.html", "Works"), ("commission.html", "Commission"), ("contact.html", "Contact")]


def head(title, desc, page, path=None, og=None, ld=None, og_type="website", og_alt=None):
    path = path if path is not None else ("" if page == "home" else f"{page}.html")
    url = f"{SITE}/{path}"
    og_dims = ""
    if not og and os.path.exists(f"{ROOT}assets/og/og-{page}.jpg"):
        og_dims = '\n  <meta property="og:image:width" content="1200" />\n  <meta property="og:image:height" content="630" />'
    og = og or f"{SITE}/assets/og/og-{page}.jpg"
    ld_html = "".join(f'\n  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{e(desc)}" />
  <meta name="theme-color" content="#f3eee4" />
  <link rel="canonical" href="{url}" />
  <meta property="og:site_name" content="John Akande" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:image" content="{og}" />{og_dims}
  <meta property="og:image:alt" content="{e(og_alt or title)}" />
  <meta property="og:locale" content="en_GB" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="{og_type}" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png" />
  <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <script>try{{if(sessionStorage.getItem("ja-intro"))document.documentElement.classList.add("intro-seen")}}catch(e){{}}</script>{ld_html}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="preconnect" href="https://api.fontshare.com" crossorigin />
  <link href="https://api.fontshare.com/v2/css?f[]=gambarino@400&display=swap" rel="stylesheet" />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;1,400&family=Italiana&family=Roboto+Mono:wght@300;400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body data-page="{page}">
  <div class="loader" aria-hidden="true">
    <div class="loader__name"><span style="--i:0">J</span><span style="--i:1">O</span><span style="--i:2">H</span><span style="--i:3">N</span><span style="--i:4">&nbsp;</span><span style="--i:5">A</span><span style="--i:6">K</span><span style="--i:7">A</span><span style="--i:8">N</span><span style="--i:9">D</span><span style="--i:10">E</span></div>
    <i class="loader__line"></i>
    <p class="loader__sub">Figurative artist &middot; Lagos</p>
  </div>
  <a class="skip" href="#main">Skip to content</a>
"""


def nav(active):
    cur = lambda f: ' aria-current="page"' if f == active else ""
    menu_links = "\n".join(
        f'      <li style="--i:{i}"><a href="{f}"{cur(f)}><span class="mono">0{i+1}</span>{label}<i aria-hidden="true"></i></a></li>'
        for i, (f, label) in enumerate(PAGES)
    )
    return f"""
  <!-- NAVIGATION -->
  <header class="nav" data-nav>
    <div class="nav__inner">
      <a class="nav__brand" href="index.html" aria-label="John Akande, home">John Akande</a>
      <nav class="nav__links" aria-label="Primary">
        <a href="about.html"{cur("about.html")}>About</a>
        <a href="works.html"{cur("works.html")}>Works</a>
        <a href="commission.html"{cur("commission.html")}>Commission</a>
        <a class="nav__cta" href="contact.html"{cur("contact.html")}><span>Contact</span></a>
      </nav>
      <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="menu" data-menu-toggle>
        <span class="nav__toggle-label">Menu</span><span class="nav__toggle-icon" aria-hidden="true"><i></i><i></i></span>
      </button>
    </div>
  </header>

  <div class="menu" id="menu" data-menu>
    <p class="menu__eyebrow mono">Menu</p>
    <ol class="menu__list">
{menu_links}
    </ol>
    <div class="menu__foot">
      <a class="btn btn--light menu__cta" href="contact.html">Start an enquiry <span class="btn__arrow" aria-hidden="true"></span></a>
      <div class="menu__meta mono">
        <span><a href="{IG}" target="_blank" rel="noopener">Instagram</a> &middot; <a href="{TH}" target="_blank" rel="noopener">Threads</a></span>
        <span>Lagos &middot; <span data-clock>--:--</span> WAT</span>
      </div>
    </div>
  </div>
"""


# Answers stick to what the site already states; add John's own policies here as they are confirmed.
FAQS = [
    ("How do I buy a painting?",
     'Open any painting in the <a class="link" href="works.html">catalogue</a> and press &ldquo;Enquire about this work&rdquo;, or use the <a class="link" href="contact.html">contact form</a>. John replies personally to confirm availability, the final price and the next steps.'),
    ("What currency are the prices in?",
     "Prices are set in US dollars. The currency switch on the Works page shows approximate amounts in euros, pounds and naira, converted at the day&rsquo;s rate; the final price is agreed in US dollars."),
    ("Can I commission a painting?",
     'Yes. Share your idea, the space it&rsquo;s for and the size you imagine, and the size, price and timeline are agreed together before work begins. See <a class="link" href="commission.html">how commissions work</a>.'),
    ("How is a painting delivered?",
     "Collection or delivery is arranged with each collector. Tell John where you&rsquo;re based when you enquire, and he&rsquo;ll confirm the options and costs."),
    ("What are the paintings made with, and how big are they?",
     "John works primarily in acrylic on canvas. Catalogue works range from 28 &times; 24 in to 7 &times; 5 ft; each painting&rsquo;s page lists its size in inches and centimetres."),
    ("How do I pay for a painting?",
     'By bank transfer to John&rsquo;s Access Bank accounts: the naira account for payments in naira, or the domiciliary account (with its SWIFT code) for international payments. Please confirm availability and the final price with John before paying. <a class="link" href="contact.html#payment">See payment details</a>.'),
    ("Does John paint live at events?",
     'Yes. Live painting turns the music and movement of an event into a finished canvas. Choose &ldquo;Live painting&rdquo; on the <a class="link" href="contact.html?type=live">contact form</a> to ask about a date.'),
]
FAQ_LD = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", html.unescape(a))}}
    for q, a in FAQS]}

def faq_section():
    items = "\n".join(f"""        <details class="faq__item"{' open' if i == 0 else ''}>
          <summary><span class="mono faq__n">{i + 1:02d}</span><span class="faq__q">{e(q)}</span><i aria-hidden="true"></i></summary>
          <div class="faq__a"><p>{a}</p></div>
        </details>""" for i, (q, a) in enumerate(FAQS))
    return f"""
  <!-- FAQ -->
  <section class="faq paper" aria-labelledby="faq-title">
    <div class="faq__head">
      <p class="mono eyebrow reveal">Questions</p>
      <h2 class="reveal" id="faq-title">Frequently <em>asked.</em></h2>
      <p class="mono faq__more reveal">Can&rsquo;t find what you need? <a class="link" href="contact.html">Ask John directly</a>.</p>
    </div>
    <div class="faq__list reveal">
{items}
    </div>
  </section>
"""


def footer(cta=True, faq=False):
    A = '<span class="btn__arrow" aria-hidden="true"></span>'
    ways = [("acquisition", "Acquire", "an available painting"), ("commission", "Commission", "a work made for you"),
            ("exhibition", "Exhibit", "shows, fairs &amp; press"), ("live", "Live painting", "at your event")]
    ways_html = "\n".join(
        f'''        <a class="cta__way" href="contact.html?type={v}"><span class="mono">0{i+1}</span><strong>{t}</strong><em class="mono">{d}</em><i aria-hidden="true">&nearr;</i></a>'''
        for i, (v, t, d) in enumerate(ways))
    cta_html = f"""
  <!-- CALL TO ACTION -->
  <section class="cta" aria-labelledby="cta-title">
    <div class="cta__bg" aria-hidden="true">{pic("rhythm-of-our-heritage", "", "100vw")}</div>
    <div class="cta__inner">
      <div class="cta__copy">
        <p class="mono eyebrow reveal">Acquisitions &amp; commissions</p>
        <h2 class="cta__title reveal" id="cta-title">Bring a painting <em>home.</em></h2>
        <p class="mono cta__lede reveal">{N_AVAIL_WORD} original paintings are available now, and new works can be made to commission in John&rsquo;s Lagos studio. Every enquiry is answered by John personally.</p>
        <div class="cta__actions reveal">
          <a class="btn btn--light" href="contact.html">Start an enquiry {A}</a>
          <a class="btn btn--gold" href="works.html">Browse available works {A}</a>
        </div>
      </div>
      <nav class="cta__panel reveal" aria-label="Ways to work with John">
        <p class="mono cta__panel-title">How can John help?</p>
{ways_html}
      </nav>
    </div>
  </section>
""" if cta else ""
    return cta_html + (faq_section() if faq else "") + f"""
  <!-- FOOTER -->
  <footer class="foot">
    <a class="foot__mark" href="index.html" aria-label="John Akande, home">John Akande</a>
    <div class="foot__grid">
      <div class="foot__about">
        <p>Contemporary Nigerian figurative artist exploring music, identity and the complexities of everyday life, in acrylic on canvas.</p>
        <a class="foot__ig" href="{IG}" target="_blank" rel="noopener"><span class="mono">Follow the studio</span><span>@akandejjohn <i aria-hidden="true">&nearr;</i></span></a>
      </div>
      <nav class="foot__col" aria-label="Footer">
        <span class="mono foot__label">Explore</span>
        <a href="index.html">Home</a>
        <a href="about.html">About</a>
        <a href="works.html">Works</a>
        <a href="commission.html">Commission</a>
        <a href="contact.html">Contact</a>
      </nav>
      <div class="foot__col">
        <span class="mono foot__label">Enquiries</span>
        <a href="contact.html?type=acquisition">Acquire a work</a>
        <a href="contact.html?type=commission">Commissions</a>
        <a href="contact.html?type=exhibition">Exhibitions &amp; press</a>
        <a href="contact.html?type=live">Live painting</a>
      </div>
      <div class="foot__col">
        <span class="mono foot__label">Studio</span>
        <span>Lagos, Nigeria</span>
        <span class="mono foot__time"><i aria-hidden="true"></i><span data-clock>--:--</span> WAT</span>
        <a href="{IG}" target="_blank" rel="noopener">Instagram &nearr;</a>
        <a href="{TH}" target="_blank" rel="noopener">Threads &nearr;</a>
      </div>
    </div>
    <div class="foot__base mono">
      <span>&copy; <span data-year>2026</span> John Akande.</span>
      <nav class="foot__legal" aria-label="Legal"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></nav>
      <a href="#top" class="foot__top" aria-label="Back to top"><span>Top</span><i aria-hidden="true"></i></a>
    </div>
  </footer>

  <!-- CREDIT -->
  <div class="ojdzn-credit">
    <span>Built by</span>
    <a href="https://ojdzn.vercel.app/?ref=akandejjohn" target="_blank" rel="noopener" aria-label="oj.dzn, view portfolio (opens in a new tab)"><img src="/assets/img/ojdzn-logo.webp" alt="oj.dzn" width="68" height="18" loading="lazy" decoding="async" /></a>
  </div>
"""


LIGHTBOX = """
  <!-- LIGHTBOX -->
  <dialog class="lightbox" data-lightbox-dialog aria-label="Artwork viewer">
    <button class="lightbox__close mono" data-lightbox-close>Close &times;</button>
    <figure>
      <img alt="" data-lb-img />
      <figcaption>
        <strong data-lb-title></strong>
        <span class="mono" data-lb-meta></span>
        <p data-lb-note></p>
        <a class="link" data-lb-enquire hidden>Enquire about this work &rarr;</a>
      </figcaption>
    </figure>
  </dialog>
"""

END = """
  <script src="script.js" defer></script>
  <script src="/_vercel/insights/script.js" defer></script>
</body>
</html>
"""


def work_card(row, extra_cls="", lazy=True, sizes="(max-width: 760px) 92vw, (max-width: 1000px) 46vw, 31vw"):
    slug, title, size, price, sold, (w, h) = row[:6]
    studio = slug.endswith("studio")
    period, year = extra(row).get("period", "recent"), extra(row).get("year", "")
    usd = price.strip("$").replace(",", "")
    status = ('<span class="work__sold">Sold</span>' if sold else
              f'<span class="work__price" data-usd="{usd}">{e(price)}</span>' if price else '<span class="work__price">Price on request</span>')
    alt = ("Rhythm of Our Heritage leaning against a white studio wall, before framing" if studio
           else f"{title}, acrylic on canvas by John Akande")
    cap = "Before framing" if studio else f"{size} · Acrylic on canvas" + (f" · {year}" if year else "")
    href = f"works/{page_slug(slug)}.html"
    return f"""        <figure class="work{extra_cls} reveal" data-status="{'sold' if sold else 'available'}" data-period="{period}" data-usd-sort="{usd_of(row)}"{' data-studio' if studio else ''}>
          <a class="work__media" href="{href}" tabindex="-1" aria-hidden="true">
            {pic(slug, e(alt), sizes, lazy=lazy)}
          </a>
          <figcaption>
            <a class="work__title" href="{href}">{e(title)}</a>
            {status}
            <span class="work__meta mono">{e(cap)}</span>
          </figcaption>
        </figure>"""


def extra(row):
    """Optional 7th field of a works.json row: {"period": "recent" | "old", "year": "2025"}."""
    return row[6] if len(row) > 6 else {}

def usd_of(row):
    return int(row[3].strip("$").replace(",", "")) if row[3] else 0

by_slug = {r[0]: r for r in META}
paintings = [r for r in META if not r[0].endswith("studio")]
n_total = len(paintings)
n_sold = sum(1 for r in paintings if r[4])
n_avail = n_total - n_sold
n_old = sum(1 for r in paintings if extra(r).get("period") == "old")
n_recent = n_total - n_old
N_AVAIL_WORD = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'][n_avail - 1].capitalize() if n_avail <= 20 else str(n_avail)


HS = ["rhythm-of-our-heritage", "young-virtuoso-i", "where-it-began-i", "where-music-takes-root", "my-fathers-footstep-i",
      "rhythm-unites-us-i", "young-virtuoso-iii", "quiet-beginning-i", "when-time-was-simple"]
HS_MOBILE = 5  # phones show only the first five, then a button to the Works page
def sel_row(i, slug):
    slug_, title, size, price, sold, (w, h) = by_slug[slug][:6]
    status = '<span class="sel__sold">Sold</span>' if sold else '<span class="sel__price">Available</span>'
    return f"""          <li{' class="sel__extra"' if i >= HS_MOBILE else ''}>
            <a class="sel__row" data-sel="{i}" data-title="{e(title)}" href="works/{slug}.html">
              {pic(slug, "", "72px", cls="sel__thumb")}
              <span class="mono sel__n">{i+1:02d}</span>
              <span class="sel__title">{e(title)}</span>
              <span class="mono sel__size">{e(size)}</span>
              {status}
              <i class="sel__go" aria-hidden="true"></i>
            </a>
          </li>"""
def sel_slide(i, slug):
    return "            " + pic(slug, "", "(min-width: 961px) 34vw, 1px", cls="sel__img" + (" is-active" if i == 0 else ""), lazy=i != 0, attrs=f' data-sel-img="{i}"')
sel_rows = "\n".join(sel_row(i, s) for i, s in enumerate(HS))
sel_slides = "\n".join(sel_slide(i, s) for i, s in enumerate(HS))
first_title = e(by_slug[HS[0]][1]); first_size = e(by_slug[HS[0]][2])

# ---------------------------------------------------------------- HOME
titles = ["Rhythm of Our Heritage", "Fear of the Unknown", "Young Virtuoso", "Where It Began", "Rhythm Unites Us",
          "Where Music Takes Root", "Quiet Beginning", "When Time Was Simple", "My Father’s Footstep"]
marq = "".join(f"<span>{e(t)}</span><i aria-hidden=\"true\">&#10022;</i>" for t in titles)

home = head("John Akande — Nigerian Figurative Artist & Painter, Lagos",
            "John Akande (@akandejjohn) is a Nigerian figurative artist based in Lagos whose paintings explore the relationship between visual art and sound.",
            "home", ld=[PERSON_LD, {"@context": "https://schema.org", "@type": "WebSite", "name": "John Akande", "url": SITE + "/"}, FAQ_LD]) + nav("index.html") + f"""
  <main id="main">
    <!-- HERO -->
    <section class="hero paper" id="top">
      <p class="hero__eyebrow mono reveal">Figurative painter &middot; Lagos, Nigeria</p>
      <h1 class="hero__name" aria-label="John Akande">
        <span class="split" data-split>JOHN AKANDE</span>
      </h1>
      <p class="hero__tag mono reveal">Paintings where sound becomes colour &mdash;<br />expressing Black culture, its identity, and the music that carries it.</p>
      <div class="hero__stage" data-parallax>
        <button class="float f1" data-speed="-0.35" style="--r:-6deg" data-lightbox data-src="{big("young-virtuoso-i")}" data-title="Young Virtuoso I" data-meta="30 × 40 in · Acrylic on canvas · Available" data-note="A girl in pink plays the violin among the instruments of a quiet interior." data-enquire="Young Virtuoso I">
          {pic("young-virtuoso-i", "Young Virtuoso I: a girl in a pink dress plays the violin", "(max-width: 760px) 1px, 270px", lazy=False)}
        </button>
        <div class="float float--ghost f2" data-speed="0.12" style="--r:4deg" aria-hidden="true">
          <img src="{mid("young-virtuoso-i")}" alt="" loading="lazy" decoding="async" />
        </div>
        <button class="float f3" data-speed="-0.5" style="--r:5deg" data-lightbox data-src="{big("my-fathers-footstep-i")}" data-title="My Father’s Footstep I" data-meta="42 × 60 in · Acrylic on canvas · Available" data-note="A boy rests beside a red cello in the warm light of a window." data-enquire="My Father’s Footstep I">
          {pic("my-fathers-footstep-i", "My Father’s Footstep I: a boy asleep beside a red cello", "(max-width: 760px) 1px, 290px", lazy=False)}
        </button>
        <div class="float float--ghost f4" data-speed="0.1" style="--r:-4deg" aria-hidden="true">
          <img src="{mid("my-fathers-footstep-i")}" alt="" loading="lazy" decoding="async" />
        </div>
        <figure class="hero__media" data-hero-media>
          <video class="hero__video" src="assets/video/hero-loop.mp4" poster="assets/img/hero-poster.jpg" autoplay muted loop playsinline preload="auto" aria-label="John Akande painting in his studio"></video>
          <span class="hero__live mono"><i></i>In the studio, Lagos</span>
          <button class="hero__mute" type="button" data-hero-mute aria-pressed="false" aria-label="Unmute">
            <svg class="hero__mute-off" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 9.5l5 5m0-5l-5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            <svg class="hero__mute-on" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </button>
          <audio data-hero-audio src="assets/video/hero-audio.m4a" loop preload="none"></audio>
        </figure>
      </div>
      <div class="hero__actions reveal">
        <a class="btn" href="works.html">View the works <span class="btn__arrow" aria-hidden="true"></span></a>
        <a class="btn btn--ghost" href="commission.html">Commission a piece <span class="btn__arrow" aria-hidden="true"></span></a>
      </div>
    </section>

    <!-- BRIEF ABOUT -->
    <section class="intro paper" id="about-brief" aria-labelledby="intro-title">
      <figure class="intro__img reveal">
        {pic("john-akande", "Portrait of John Akande in a black-and-white tweed jacket, hand at his chin", "(max-width: 860px) 92vw, 40vw")}
        <figcaption class="mono">John Akande &mdash; Lagos, Nigeria</figcaption>
      </figure>
      <div class="intro__body">
        <p class="mono eyebrow reveal">About the artist</p>
        <p class="intro__lede reveal" id="intro-title">John Akande is a contemporary Nigerian figurative artist whose practice explores human expression, cultural identity, music and the complexities of everyday life.</p>
        <div class="intro__cols mono reveal">
          <p>Formally trained at <b>Yaba College of Technology, Lagos</b>, he works primarily in <b>acrylic on canvas</b>, alongside mixed media, combining <b>realism</b> and <b>expressionism</b> to build emotionally engaging visual narratives.</p>
          <p>Music holds a significant place in his practice. His works have been exhibited in <b>Nigeria</b> and internationally, in group exhibitions and online presentations.</p>
        </div>
        <a class="btn btn--ghost reveal" href="about.html">Read the biography <span class="btn__arrow" aria-hidden="true"></span></a>
      </div>
    </section>

    <!-- MARQUEE -->
    <div class="marquee" aria-hidden="true">
      <div class="marquee__track">{marq}{marq}</div>
    </div>

    <!-- SELECTED WORKS -->
    <section class="sel paper" id="featured" aria-labelledby="sel-title" data-sel-root>
      <header class="sel__head">
        <div>
          <p class="mono eyebrow reveal">The catalogue</p>
          <h2 class="reveal" id="sel-title">Selected Works</h2>
        </div>
        <div class="sel__intro reveal">
          <p class="mono">A selection from a body of work on music, memory and belonging, in acrylic on canvas.</p>
        </div>
      </header>
      <div class="sel__body">
        <div class="sel__stage reveal" aria-hidden="true">
          <div class="sel__frame">
{sel_slides}
          </div>
          <div class="sel__caption">
            <span class="mono sel__count"><b data-sel-index>01</b> / {len(HS):02d}</span>
            <span class="sel__now" data-sel-title>{first_title}</span>
            <span class="mono sel__nowsize" data-sel-size>{first_size} &middot; Acrylic on canvas</span>
          </div>
        </div>
        <div class="sel__side">
          <ol class="sel__list">
{sel_rows}
          </ol>
          <div class="sel__more reveal">
            <p class="mono">{n_total} paintings in the catalogue. <b>{n_avail} available.</b></p>
            <a class="btn" href="works.html">View all works <span class="btn__arrow" aria-hidden="true"></span></a>
          </div>
        </div>
      </div>
    </section>

  </main>
""" + footer(faq=True) + LIGHTBOX + END

# ---------------------------------------------------------------- WORKS
works_cards = [work_card(META[0], " work--feature", lazy=False), work_card(META[1], lazy=False)]
works_cards += [work_card(r) for r in META[2:]]
works = head("Paintings for Sale — John Akande, Acrylic on Canvas",
             f"Browse {n_total} original acrylic paintings by Nigerian artist John Akande, on music, heritage and memory. Sizes, prices in USD, EUR, GBP or NGN, and availability.",
             "works") + nav("works.html") + f"""
  <main id="main" class="paper">
    <header class="page-head" id="top">
      <p class="mono eyebrow reveal">Catalogue &middot; Acrylic on canvas</p>
      <h1 class="page-head__title reveal">Works</h1>
      <div class="page-head__body mono reveal">
        <p>{STATEMENT}</p>
        <p>{STATEMENT_2}</p>
        <p class="page-head__sig">&mdash; John Akande</p>
      </div>
    </header>

    <section class="works" aria-label="All works">
      <div class="toolbar reveal">
        <div class="toolbar__filters">
          <div class="filters" role="group" aria-label="Show works from" data-filter-group="period">
            <span class="mono filters__label">Works</span>
            <button class="chip" aria-pressed="true" data-filter="all">All <span>{n_total}</span></button>
            <button class="chip" aria-pressed="false" data-filter="recent">Recent <span>{n_recent}</span></button>
            <button class="chip" aria-pressed="false" data-filter="old">Earlier <span>{n_old}</span></button>
          </div>
          <div class="filters" role="group" aria-label="Filter by availability" data-filter-group="status">
            <span class="mono filters__label">Status</span>
            <button class="chip" aria-pressed="true" data-filter="all">All</button>
            <button class="chip" aria-pressed="false" data-filter="available">Available <span>{n_avail}</span></button>
            <button class="chip" aria-pressed="false" data-filter="sold">Sold <span>{n_sold}</span></button>
          </div>
          <label class="sort">
            <span class="mono filters__label">Sort</span>
            <select data-sort>
              <option value="featured">Featured</option>
              <option value="price-asc">Price: low to high</option>
              <option value="price-desc">Price: high to low</option>
            </select>
          </label>
        </div>
{currency_switch()}
      </div>
      <p class="mono works__count" data-works-count aria-live="polite">Showing all {n_total} works</p>
      <div class="works__grid" data-works>
{chr(10).join(works_cards)}
      </div>
    </section>
  </main>
""" + footer() + LIGHTBOX + END

# ---------------------------------------------------------------- ABOUT
about = head("About John Akande — Nigerian Figurative Artist, Lagos",
             "John Akande (b. Lagos, Nigeria) is a contemporary Nigerian figurative artist exploring human expression, cultural identity, music and everyday life.",
             "about", ld=[PERSON_LD]) + nav("about.html") + f"""
  <main id="main">
    <div class="paper">
    <header class="page-head" id="top">
      <p class="mono eyebrow reveal">Artist biography</p>
      <h1 class="page-head__title reveal">About</h1>
      <p class="page-head__lede reveal">John Akande (b. Lagos, Nigeria) is a contemporary Nigerian figurative artist whose practice explores human expression, cultural identity, music and the complexities of everyday life.</p>
      <figure class="page-head__portrait reveal">
        {pic("john-akande", "Portrait of John Akande in a black-and-white tweed jacket, hand at his chin", "(max-width: 860px) 92vw, 26rem", lazy=False)}
        <figcaption class="mono">John Akande</figcaption>
      </figure>
    </header>

    <section class="bio" aria-label="Biography">
      <div class="bio__side">
        <dl class="bio__facts mono reveal">
          <div><dt>Born</dt><dd>Lagos, Nigeria</dd></div>
          <div><dt>Education</dt><dd>Yaba College of Technology, Lagos</dd></div>
          <div><dt>Medium</dt><dd>Acrylic on canvas, mixed media</dd></div>
          <div><dt>Exhibited</dt><dd>Nigeria &middot; International &middot; Online</dd></div>
        </dl>
      </div>
      <div class="bio__text">
          <p class="reveal">His artistic journey is rooted in his early exposure to the cultural richness of Lagos and a longstanding fascination with the ways people express, experience and connect with one another. He received his formal art education at Yaba College of Technology, Lagos, where he developed a foundation in visual art and figurative representation.</p>
          <p class="reveal">Working primarily with acrylic on canvas, alongside mixed-media approaches, John Akande combines elements of realism and expressionism to construct emotionally engaging visual narratives. His paintings are distinguished by expressive brushwork, layered textures, vibrant yet deliberate colour relationships and a strong sensitivity to composition. Through the human figure, he explores themes of memory, identity, relationships, belonging and the emotional dimensions of human existence.</p>
          <p class="reveal">Music holds a significant place in his practice, informed by his personal encounters with musical environments and his appreciation of its cultural and emotional significance. His paintings frequently examine musicians, musical instruments and shared moments of musical experience, using them as subjects through which to investigate human connection, heritage and the passage of personal and collective memories.</p>
          <p class="reveal">Drawing from Nigerian cultural experiences while engaging with universal human themes, Akande seeks to create works that resonate beyond geographical and cultural boundaries. His practice reflects an ongoing commitment to storytelling through painting, using the visual language of the human figure to communicate experiences, emotions and narratives that connect people across cultures.</p>
          <p class="reveal">His works have been exhibited in Nigeria and internationally, and have featured in group exhibitions and online presentations.</p>
          <div class="bio__cta reveal">
            <a class="btn" href="works.html">See the works <span class="btn__arrow" aria-hidden="true"></span></a>
            <a class="btn btn--ghost" href="commission.html">Commission a piece <span class="btn__arrow" aria-hidden="true"></span></a>
          </div>
      </div>
    </section>
    </div>

    <!-- STUDIO FILM -->
    <section class="film" aria-labelledby="film-title">
      <div class="film__text reveal">
        <p class="mono eyebrow">Studio film &middot; 0:58</p>
        <h2 id="film-title">In the studio</h2>
        <p class="mono">John at work in Lagos, talking about where the music in his paintings comes from: growing up without access to instruments, and the friend&rsquo;s home where he found them.</p>
      </div>
      <div class="phone film__video reveal">
        <video data-story src="assets/video/studio-story.mp4" poster="assets/img/studio-poster.jpg" playsinline preload="none"></video>
        <button class="play" data-play aria-label="Play the studio film">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
          <span class="mono">Play &middot; 0:58</span>
        </button>
      </div>
    </section>

    <!-- ARTIST STATEMENT -->
    <section class="statement" id="statement" aria-labelledby="statement-title">
      <header class="statement__head">
        <p class="mono eyebrow reveal">In his own words</p>
        <h2 class="reveal" id="statement-title">Artist Statement</h2>
        <blockquote class="statement__pull reveal">&ldquo;I see painting as a means of giving visual form to experiences that words cannot always fully express.&rdquo;</blockquote>
      </header>
      <div class="statement__text">
          <p class="reveal">My artistic practice explores the relationship between music, human expression, cultural identity and the experiences that shape everyday life. Working primarily through figurative painting, I am interested in the human figure as a vessel for stories, emotions and shared experiences. My paintings draw from observations of life, personal memories and cultural encounters, translating moments of human existence into visual narratives.</p>
          <p class="reveal">Music occupies a central place in my practice, not merely as a subject to be represented but as a language through which I explore human connection, memory, emotion and belonging. My early encounters with musical environments and the cultural significance of music in everyday life have shaped my interest in the relationship between people, instruments and the spaces they inhabit. I am particularly drawn to the gestures, expressions and quiet interactions that surround musical experiences, often exploring what exists beyond the performance itself.</p>
          <p class="reveal">Works such as <i>Rhythm of Our Heritage</i> (2026), <i>Little Dreamer II</i> (2025) and <i>My Father’s Footsteps II</i> examine different dimensions of this relationship. While some compositions capture the collective experience of music-making, others focus on individual moments of reflection, aspiration and rest. Through these narratives, I seek to reveal the emotional and human experiences that often remain beneath the surface of ordinary encounters.</p>
          <p class="reveal">Rooted in my Nigerian background and influenced by the richness of African cultural life, my work also reflects a broader interest in the human condition. I draw upon the visual language of my environment, combining elements of expressionism and realism through expressive brushwork, vibrant yet considered colour relationships, texture and carefully constructed compositions.</p>
          <p class="reveal">Ultimately, my practice is an ongoing exploration of how art can preserve memories, communicate emotions and create connections between people and cultures. I see painting as a means of giving visual form to experiences that words cannot always fully express, inviting viewers to recognise something of their own humanity within the stories I tell.</p>
          <p class="statement__sig reveal">&mdash; John Akande</p>
      </div>
    </section>

    <!-- IN HIS WORDS -->
    <section class="words">
      <header class="head">
        <h2 class="reveal">From the Studio</h2>
        <p class="mono head__note reveal">From the studio film &mdash; on where the music in the paintings comes from.</p>
      </header>
      <ol class="words__list">
        <li class="reveal"><span class="mono n">01</span><q>I didn&rsquo;t have access to musical instruments for practice.</q><span class="mono who">John Akande<br /><i>Studio film</i></span></li>
        <li class="reveal"><span class="mono n">02</span><q>I was fortunate to have a friend living nearby, whose family&rsquo;s mansion was filled with various instruments.</q><span class="mono who">John Akande<br /><i>Studio film</i></span></li>
        <li class="reveal"><span class="mono n">03</span><q>I loved visiting her, and her family always welcomed me warmly.</q><span class="mono who">John Akande<br /><i>Studio film</i></span></li>
        <li class="reveal"><span class="mono n">04</span><q>Those visits provided a nurturing environment.</q><span class="mono who">John Akande<br /><i>Studio film</i></span></li>
      </ol>
    </section>

    <!-- THEMES -->
    <section class="themes">
      <h2 class="reveal">Themes &amp;<br />Practice</h2>
      <ul class="themes__list mono">
        <li class="reveal"><span>Music &amp; Sound</span><span>01</span></li>
        <li class="reveal"><span>Identity</span><span>02</span></li>
        <li class="reveal"><span>Heritage</span><span>03</span></li>
        <li class="reveal"><span>Childhood &amp; Wonder</span><span>04</span></li>
        <li class="reveal"><span>Live Painting</span><span>05</span></li>
      </ul>
    </section>

    <!-- PRESS -->
    <section class="press">
      <h2 class="reveal">Features &amp;<br />Press</h2>
      <div class="table mono">
        <div class="row row--head"><span>Publication</span><span>Feature</span><span>Section</span></div>
        <div class="row reveal"><span>Incongru Magazine</span><span>Little Dreamer II</span><span>Visual Art</span></div>
        <div class="row reveal"><span>The Guardian Nigeria</span><span>How Nigeria&rsquo;s emerging artists are&hellip;</span><span>Life</span></div>
      </div>
    </section>
  </main>
""" + footer() + END

# ---------------------------------------------------------------- CONTACT
def pay_card(title, cur, rows):
    lines = "\n".join(
        f"""            <div><dt>{e(k)}</dt><dd>{f'<span data-copy-value>{e(v)}</span><button class="pay__copy mono" type="button" data-copy aria-label="Copy {e(k.lower())} {e(v)}">Copy</button>' if k in ("Account number", "SWIFT code") else e(v)}</dd></div>"""
        for k, v in rows)
    return f"""        <article class="pay__card reveal">
          <header><h3>{e(title)}</h3><span class="mono">{e(cur)}</span></header>
          <dl class="mono">
{lines}
          </dl>
        </article>"""
pay_cards = "\n".join(pay_card(*a) for a in BANK_ACCOUNTS)

avail_opts = "\n".join(f'              <option>{e(r[1])}</option>' for r in paintings if not r[4])
types = [("acquisition", "Acquiring a work"), ("commission", "A commission"),
         ("exhibition", "An exhibition or press"), ("live", "Live painting")]
type_html = "\n".join(
    f'            <label class="chip"><input type="radio" name="type" value="{v}"{" checked" if i == 0 else ""} /> {lbl}</label>'
    for i, (v, lbl) in enumerate(types))
contact = head("Contact John Akande — Enquiries, Commissions & Payment",
               "Contact Lagos-based artist John Akande to buy a painting, commission a new work, request a print, or book an exhibition or live painting. Payment details included.",
               "contact") + nav("contact.html") + f"""
  <main id="main" class="paper">
    <header class="page-head" id="top">
      <p class="mono eyebrow reveal">Contact &middot; Lagos, Nigeria</p>
      <h1 class="page-head__title page-head__title--wide reveal">Get in <em>touch.</em></h1>
      <p class="page-head__lede page-head__lede--sm reveal">Whether you&rsquo;d like to acquire a painting, commission a new work, or invite John to exhibit or paint live, he&rsquo;d love to hear from you. Fill in the form below and John will reply to you personally.</p>
    </header>

    <section class="enquire">
      <form class="composer reveal" data-composer data-email="{EMAIL}" novalidate>
        <fieldset>
          <legend class="mono">01 &mdash; I&rsquo;m enquiring about</legend>
          <div class="chips">
{type_html}
          </div>
        </fieldset>
        <label class="field" data-work-field>
          <span class="mono">02 &mdash; Which work?</span>
          <select name="work">
              <option value="">Not sure yet</option>
{avail_opts}
          </select>
        </label>
        <label class="field">
          <span class="mono">03 &mdash; Your name <b class="field__req" aria-hidden="true">*</b></span>
          <input name="name" type="text" autocomplete="name" placeholder="Your name" required minlength="2" maxlength="80" aria-describedby="name-error" />
          <span class="field__error mono" id="name-error" data-error-for="name" hidden>Please add your name so John knows who he&rsquo;s replying to.</span>
        </label>
        <label class="field">
          <span class="mono">04 &mdash; Your message</span>
          <textarea name="message" rows="4" maxlength="2000" placeholder="Where you&rsquo;re based, timing, anything John should know"></textarea>
        </label>
        <div class="composer__preview">
          <span class="mono">Your message</span>
          <p data-preview></p>
        </div>
        <div class="composer__actions">
          <button class="btn" type="submit">Send enquiry by email <span class="btn__arrow" aria-hidden="true"></span></button>
          <p class="mono composer__status" data-status role="status" aria-live="polite"></p>
        </div>
      </form>

      <aside class="enquire__side reveal">
        <div>
          <span class="mono eyebrow">Studio</span>
          <p>Lagos, Nigeria</p>
          <p class="mono"><span data-clock>--:--</span> WAT</p>
        </div>
        <div>
          <span class="mono eyebrow">Direct</span>
          <p><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></p>
          <p><a class="link" href="{IG}" target="_blank" rel="noopener">Instagram &nearr;</a></p>
          <p><a class="link" href="{TH}" target="_blank" rel="noopener">Threads &nearr;</a></p>
        </div>
        <div>
          <span class="mono eyebrow">Available now</span>
          <p>{n_avail} of {n_total} paintings</p>
          <p><a class="link" href="works.html">Browse the catalogue &rarr;</a></p>
        </div>
      </aside>
    </section>

    <!-- PAYMENT -->
    <section class="pay" id="payment" aria-labelledby="pay-title">
      <header class="pay__head">
        <p class="mono eyebrow reveal">Payment</p>
        <h2 class="reveal" id="pay-title">Payment <em>details.</em></h2>
        <p class="mono pay__note reveal">Payment is by bank transfer. Please confirm the painting&rsquo;s availability and final price with John <b>before</b> paying, and send him your transfer receipt afterwards.</p>
      </header>
      <div class="pay__grid">
{pay_cards}
      </div>
    </section>
  </main>
""" + footer(cta=False) + END


# ---------------------------------------------------------------- COMMISSION
offers = [
    ("where-music-takes-root", "Where Music Takes Root, framed", "01", "A painting for your space",
     "An original acrylic on canvas, scaled to your wall and built around a story that matters to you."),
    ("young-virtuoso-iii", "Young Virtuoso III, framed", "02", "Portraits &amp; musicians",
     "A person, a family or a performer, painted in John&rsquo;s figurative style of bold contrast and textured layers."),
    ("studio", "John Akande at work in his Lagos studio", "03", "Live painting",
     "John paints live at your event, turning the music and movement in the room into a finished canvas."),
]
offer_html = "\n".join(f"""        <article class="offer reveal">
          <div class="offer__img">{pic(src, alt, "(max-width: 600px) 92vw, (max-width: 960px) 46vw, 31vw") if src != "studio" else f'<img src="assets/img/studio-poster.jpg" alt="{alt}" loading="lazy" decoding="async" />'}</div>
          <span class="mono offer__n">{n}</span>
          <h3>{t}</h3>
          <p class="mono">{d}</p>
        </article>""" for src, alt, n, t, d in offers)
steps = [
    ("Share your idea", "Tell John what you have in mind: the subject, the space it&rsquo;s for, and the size you imagine."),
    ("Agree the details", "Size, price and timeline are agreed together before any paint touches the canvas."),
    ("In the studio", "John paints the work by hand in his Lagos studio, in acrylic on canvas."),
    ("Delivery", "Collection or shipping of the finished painting is arranged with you."),
]
steps_html = "\n".join(f"""        <li class="reveal"><span class="steps__n">0{i+1}</span><h3>{t}</h3><p class="mono">{d}</p></li>""" for i, (t, d) in enumerate(steps))
sizes = sorted([r for r in paintings if r[3]], key=lambda r: int(r[3].strip("$").replace(",", "")))
commission = head("Commission a Painting — John Akande, Lagos",
                  "Commission an original painting, portrait or live painting from Lagos-based figurative artist John Akande.",
                  "commission") + nav("commission.html") + f"""
  <main id="main" class="paper">
    <header class="page-head" id="top">
      <p class="mono eyebrow reveal">Commissions</p>
      <h1 class="page-head__title reveal">Commission</h1>
      <p class="page-head__lede reveal">An original painting, made for you in John Akande&rsquo;s Lagos studio.</p>
    </header>

    <section class="offers" aria-labelledby="offers-title">
      <h2 class="visually-hidden" id="offers-title">What you can commission</h2>
      <div class="offers__grid">
{offer_html}
      </div>
    </section>

    <section class="process">
      <header class="head">
        <div>
          <p class="mono eyebrow reveal">The process</p>
          <h2 class="reveal">How it works</h2>
        </div>
        <p class="mono head__note reveal">For reference, catalogue works range from <b>{sizes[0][2]}</b> at {sizes[0][3]} to <b>{sizes[-1][2]}</b> at {sizes[-1][3]}.</p>
      </header>
      <ol class="steps">
{steps_html}
      </ol>
      <div class="process__cta reveal">
        <a class="btn" href="contact.html?type=commission">Start a commission <span class="btn__arrow" aria-hidden="true"></span></a>
        <a class="btn btn--ghost" href="works.html">See the works <span class="btn__arrow" aria-hidden="true"></span></a>
      </div>
    </section>
  </main>
""" + footer() + END

# ---------------------------------------------------------------- ARTWORK PAGES
def dims(size, w, h):
    """Width and height in inches; the longer side follows the photo's orientation."""
    a, b = map(int, re.findall(r"\d+", size)[:2])
    if "ft" in size:
        a, b = a * 12, b * 12
    long_, short = max(a, b), min(a, b)
    return (long_, short) if w >= h else (short, long_)

def series(title):
    return re.sub(r"\s+[IVX]+$", "", title)

NOTE_RECENT = ("Part of a body of work exploring music as a living force: how rhythm shapes identity, how performance "
               "reveals vulnerability, and how music functions as cultural memory and therapy.")
NOTE_OLD = ("An earlier work from John Akande&rsquo;s studio in Lagos, painted in acrylic on canvas with the expressive brushwork "
            "and layered colour that run through his figurative practice.")
order = [r for r in META if not r[0].endswith("studio")]
art_pages = {}
for k, row in enumerate(order):
    slug, title, size, price, sold, (w, h) = row[:6]
    year = extra(row).get("year", "")
    usd = price.strip("$").replace(",", "")
    pw, ph = dims(size, IMGS[slug]["w"], IMGS[slug]["h"])
    a_, b_ = [int(n) * (12 if "ft" in size else 1) for n in re.findall(r"\d+", size)[:2]]
    cm = f"{round(a_ * 2.54)} × {round(b_ * 2.54)} cm"
    prev_r, next_r = order[k - 1], order[(k + 1) % len(order)]
    ser = series(title)
    siblings = [r for r in order if series(r[1]) == ser and r[0] != slug]
    pool = siblings + [r for r in order[k + 1:] + order[:k] if r not in siblings and r[0] != slug]
    related = pool[:3]
    related_html = "\n".join(work_card(r, sizes="(max-width: 760px) 92vw, 31vw") for r in related)
    more_title = f"More from <em>{e(ser)}</em>" if siblings else "More from the <em>catalogue</em>"
    status_pill = '<span class="art__status art__status--sold">Sold</span>' if sold else '<span class="art__status">Available</span>'
    price_html = ('<dd class="art__sold">Sold</dd>' if sold else
                  f'<dd><span class="art__price" data-usd="{usd}">{e(price)}</span></dd>' if price else '<dd>On request</dd>')
    actions = (f'''<a class="btn" href="contact.html?type=commission">Commission a similar work <span class="btn__arrow" aria-hidden="true"></span></a>''' if sold else
               f'''<a class="btn" href="contact.html?work={e(title).replace(" ", "%20")}">Enquire about this work <span class="btn__arrow" aria-hidden="true"></span></a>''')
    studio_extra = ""
    if EMAIL:
        subj = f"Print request: {title}"
        body = (f"Hello John,\n\nI'd like to request a print of \"{title}\" ({size}, acrylic on canvas).\n\n"
                f"Preferred print size:\nWhere I'm based (for delivery):\n\nThank you.\n\n{SITE}/works/{slug}.html")
        from urllib.parse import quote
        print_btn = f'<a class="btn btn--ghost" href="mailto:{EMAIL}?subject={quote(subj)}&amp;body={quote(body)}">Request a print <span class="btn__arrow" aria-hidden="true"></span></a>'
    else:
        print_btn = ""
    if slug == "rhythm-of-our-heritage":
        studio_extra = f"""
          <figure class="art__alt">
            <button class="art__zoom" data-lightbox data-src="{big('rhythm-of-our-heritage-studio')}" data-title="Rhythm of Our Heritage" data-meta="In the studio, before framing" data-note="">
              {pic("rhythm-of-our-heritage-studio", "Rhythm of Our Heritage leaning against a white studio wall, before framing", "(max-width: 960px) 40vw, 18vw")}
            </button>
            <figcaption class="mono">In the studio, before framing</figcaption>
          </figure>"""
    ld = {
        "@context": "https://schema.org", "@type": "VisualArtwork", "name": title,
        "creator": {"@type": "Person", "name": "John Akande", "url": SITE + "/"},
        "artform": "Painting", "artMedium": "Acrylic", "artworkSurface": "Canvas", **({"dateCreated": year} if year else {}),
        "width": {"@type": "Distance", "name": f"{pw} in"}, "height": {"@type": "Distance", "name": f"{ph} in"},
        "image": f"{SITE}/{img_base(slug)}.jpg", "url": f"{SITE}/works/{slug}.html",
        "offers": {"@type": "Offer", **({"price": usd, "priceCurrency": "USD"} if price else {}), "url": f"{SITE}/works/{slug}.html",
                   "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock"},
    }
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Works", "item": f"{SITE}/works.html"},
        {"@type": "ListItem", "position": 2, "name": title, "item": f"{SITE}/works/{slug}.html"}]}
    desc = (f"{title} by Nigerian artist John Akande: an original {size} acrylic on canvas painting. "
            + ("Sold; prints and similar commissions available." if sold else f"Available{', ' + price if price else ''}. Enquire or request a print."))
    doc = head(f"{e(title)} — Painting by John Akande", desc, "works", path=f"works/{slug}.html",
               og=f"{SITE}/{img_base(slug)}.jpg", ld=[ld, crumbs], og_type="article",
               og_alt=f"{title}, acrylic on canvas by John Akande") + nav("works.html") + f"""
  <main id="main" class="paper">
    <article class="art" id="top">
      <nav class="art__crumbs mono" aria-label="Breadcrumb">
        <a href="works.html">Works</a><span aria-hidden="true">/</span><span aria-current="page">{e(title)}</span>
      </nav>
      <div class="art__grid">
        <div class="art__media">
          <button class="art__zoom art__main" data-lightbox data-src="{big(slug)}" data-title="{e(title)}" data-meta="{e(size)} · Acrylic on canvas" data-note="" aria-label="View {e(title)} larger">
            {pic(slug, f"{e(title)}, acrylic on canvas by John Akande", "(max-width: 960px) 92vw, 55vw", lazy=False)}
            <span class="art__hint mono" aria-hidden="true">View larger</span>
          </button>{studio_extra}
        </div>
        <div class="art__info">
          <p class="mono eyebrow">Acrylic on canvas{f" &middot; {e(ser)} series" if siblings else ""}{f" &middot; {year}" if year else ""}</p>
          <h1 class="art__title">{e(title)}</h1>
          {status_pill}
          <dl class="art__facts mono">
            <div><dt>Size</dt><dd>{e(size)} <span>({cm})</span></dd></div>
            <div><dt>Medium</dt><dd>Acrylic on canvas</dd></div>{f'<div><dt>Year</dt><dd>{year}</dd></div>' if year else ""}
            <div><dt>Price</dt>{price_html}</div>
            <div><dt>Artist</dt><dd>John Akande, Lagos</dd></div>
          </dl>
{"" if sold or not price else currency_switch(compact=True)}
          <p class="art__note">{NOTE_OLD if extra(row).get("period") == "old" else NOTE_RECENT}</p>
          <div class="art__actions">
            {actions}
            {print_btn}
          </div>
          {"" if sold else '<p class="art__pay mono">Payment by bank transfer. <a class="link" href="contact.html#payment">See payment details</a></p>'}
        </div>
      </div>
    </article>


    <section class="related" aria-labelledby="related-title">
      <header class="head">
        <h2 class="reveal" id="related-title">{more_title}</h2>
        <a class="btn btn--ghost reveal" href="works.html">All works <span class="btn__arrow" aria-hidden="true"></span></a>
      </header>
      <div class="related__grid">
{related_html}
      </div>
      <nav class="art__pager" aria-label="Previous and next work">
        <a href="works/{prev_r[0]}.html" rel="prev"><span class="mono">Previous</span><strong>{e(prev_r[1])}</strong></a>
        <a href="works/{next_r[0]}.html" rel="next"><span class="mono">Next</span><strong>{e(next_r[1])}</strong></a>
      </nav>
    </section>
  </main>
""" + footer() + LIGHTBOX + END
    art_pages[f"works/{slug}.html"] = doc

# ---------------------------------------------------------------- 404
notfound = head("Page not found — John Akande", "This page could not be found.", "404", path="404.html", og=f"{SITE}/assets/og/og-home.jpg") + nav("") + f"""
  <main id="main" class="paper nf">
    <div class="nf__inner" id="top">
      <p class="mono eyebrow">Error 404</p>
      <h1 class="nf__title">This page has left <em>the gallery.</em></h1>
      <p class="mono nf__text">The link may be old, or the page may have moved. The paintings are all still here.</p>
      <div class="nf__actions">
        <a class="btn" href="works.html">View the works <span class="btn__arrow" aria-hidden="true"></span></a>
        <a class="btn btn--ghost" href="index.html">Back to home <span class="btn__arrow" aria-hidden="true"></span></a>
      </div>
    </div>
    <div class="nf__art" aria-hidden="true">{pic("quiet-beginning-i", "", "(max-width: 860px) 70vw, 30vw", lazy=False)}</div>
  </main>
""" + footer(cta=False) + END
notfound = notfound.replace('<meta name="description"', '<meta name="robots" content="noindex" />\n  <meta name="description"', 1)

# ---------------------------------------------------------------- PRIVACY + TERMS
# Plain-language summaries of what the site actually does. They are a starting point for John
# to review, not legal advice; update them if the site starts collecting anything new.
LEGAL_UPDATED = "26 November 2026"

def legal_page(slug, title, lede, sections, desc):
    toc = "\n".join(f'          <li><a href="{slug}.html#{sid}">{e(h)}</a></li>' for sid, h, _ in sections)
    body = "\n".join(f"""        <section class="legal__sec" id="{sid}" aria-labelledby="{sid}-h">
          <h2 id="{sid}-h">{e(h)}</h2>
{html_}
        </section>""" for sid, h, html_ in sections)
    return head(f"{title} — John Akande", desc, slug, og=f"{SITE}/assets/og/og-home.jpg") + nav("") + f"""
  <main id="main" class="paper">
    <header class="page-head" id="top">
      <p class="mono eyebrow reveal">Last updated {LEGAL_UPDATED}</p>
      <h1 class="page-head__title reveal">{title}</h1>
      <p class="page-head__lede page-head__lede--sm reveal">{lede}</p>
    </header>
    <div class="legal">
      <nav class="legal__toc mono" aria-label="On this page">
        <p class="eyebrow">On this page</p>
        <ol>
{toc}
        </ol>
      </nav>
      <div class="legal__body">
{body}
      </div>
    </div>
  </main>
""" + footer(cta=False) + END

P = lambda *ps: "\n".join(f"          <p>{p}</p>" for p in ps)
UL = lambda *xs: "          <ul>\n" + "\n".join(f"            <li>{x}</li>" for x in xs) + "\n          </ul>"

privacy = legal_page("privacy", "Privacy Policy",
    "How this website handles information about you. In short: it has no accounts, sets no cookies and does not sell or share your details.",
    [
        ("who", "Who we are", P(
            "This website, johnakande.studio, is the portfolio of John Tobi Akande, a figurative artist based in Lagos, Nigeria. In this policy, &ldquo;we&rdquo; and &ldquo;John&rdquo; mean him.",
            f'For any question about your information, email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>.')),
        ("collect", "What we collect", P(
            "You can browse the whole site without giving us any personal information. The only personal information John receives is what you choose to send him:")
            + "\n" + UL(
            "<b>Enquiries and print requests.</b> The contact form and the &ldquo;Request a print&rdquo; button do not send anything through this website. They open your own email app with a message already written; nothing is sent until you press send there. John then receives your email, which includes your email address, your name if you give it, and your message.",
            "<b>Payments.</b> If you buy a painting, John receives the bank transfer details your bank shares with him and any receipt you send.")),
        ("use", "How we use it", P(
            "John uses your messages only to reply to you, to arrange a sale, commission, print, exhibition or live painting, and to keep records of sales. He does not sell, rent or trade your information, and he does not add you to a mailing list without asking.")),
        ("cookies", "Cookies and browser storage", P(
            "This website does not set cookies, so there is no cookie banner. It saves three small preferences in your own browser, which never leave your device:")
            + "\n" + UL(
            "the currency you chose for prices on the Works page;",
            "the day&rsquo;s exchange rates, so they are not downloaded again for 12 hours;",
            "a note that the opening animation has already played during this visit.")
            + "\n" + P("You can clear these at any time by clearing your browser&rsquo;s site data.")),
        ("others", "Services that help run the site", P(
            "Like any website, loading these pages means your browser connects to the services below. They receive technical information such as your IP address and browser type, under their own privacy policies:")
            + "\n" + UL(
            "<b>Vercel</b>, which hosts the website and keeps standard server logs. Vercel Web Analytics may also count page visits; it does not use cookies and reports only totals, not individual visitors.",
            "<b>Google Fonts</b> and <b>Fontshare</b>, which provide the typefaces.",
            "<b>open.er-api.com</b>, which provides exchange rates when prices are shown in another currency.",
            "<b>Instagram</b> and <b>Threads</b>, only if you follow a link to them.")),
        ("keep", "How long we keep it", P(
            "Emails are kept for as long as they are useful for replying to you and for John&rsquo;s sales and tax records, and are then deleted.")),
        ("rights", "Your choices", P(
            f'You can ask John to see the information he holds about you, to correct it, or to delete it, by emailing <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>. He will reply as soon as he can.')),
        ("changes", "Changes to this policy", P(
            "If this policy changes, the new version will be posted on this page with a new &ldquo;last updated&rdquo; date.")),
    ],
    "How johnakande.studio handles your information: no accounts, no cookies, and enquiries go straight to John by email.")

terms = legal_page("terms", "Terms of Use",
    "The terms for using this website and for enquiring about, commissioning or buying John Akande&rsquo;s work.",
    [
        ("site", "Using this website", P(
            "By using johnakande.studio you agree to these terms. The website is provided so you can view John Akande&rsquo;s work and contact him. Please don&rsquo;t misuse it, for example by trying to disrupt it or by copying its content in bulk.")),
        ("copyright", "Artwork and copyright", P(
            "All paintings, photographs, videos and text on this website are &copy; John Akande unless stated otherwise. You may share links to the website and its pages. You may not copy, print, sell or reuse the images, or use them to train software, without John&rsquo;s written permission.",
            "Buying a painting gives you ownership of that physical painting. The copyright stays with John unless you both agree otherwise in writing.")),
        ("prices", "Prices and availability", P(
            "Prices on this website are set in US dollars. Amounts shown in euros, pounds or naira are approximate conversions at the day&rsquo;s exchange rate, for guidance only. The final price is the one John confirms to you.",
            "Prices and availability can change, and a painting shown as available may already be reserved. A painting is only reserved for you once John has confirmed it in writing.")),
        ("buying", "Buying a painting", P(
            "To buy a painting, enquire first. John will confirm the price, availability and arrangements before you pay. Payment is by bank transfer to the accounts on the Contact page; please only pay after John has confirmed the sale, and send him your receipt.",
            f'John will only ever ask you to pay into the accounts listed on this website. If you are asked to pay anywhere else, or by anyone else, do not pay and email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>.',
            "Collection, delivery, shipping costs and any returns are agreed with John for each sale.")),
        ("commissions", "Commissions and prints", P(
            "For a commissioned painting, the subject, size, price, timeline and payment stages are agreed with John in writing before work begins.",
            "Prints are made on request. The available sizes, price and delivery are confirmed by John when you ask.")),
        ("links", "Other websites", P(
            "This website links to other services, such as Instagram and Threads. John is not responsible for their content or how they handle your information.")),
        ("liability", "Accuracy of information", P(
            "John takes care to describe each work accurately. Colours on screen can differ from the painting itself, and sizes are approximate. If anything matters to your decision, ask John before you buy.")),
        ("contact", "Contact and changes", P(
            f'Questions about these terms: <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>. If these terms change, the new version will be posted here with a new &ldquo;last updated&rdquo; date.')),
    ],
    "Terms for using johnakande.studio and for enquiring about, commissioning or buying John Akande's paintings and prints.")

pages = {"privacy.html": privacy, "terms.html": terms, "index.html": home, "works.html": works, "about.html": about, "contact.html": contact,
         "commission.html": commission, "404.html": notfound, **art_pages}
os.makedirs(ROOT + "works", exist_ok=True)
for name, doc in pages.items():
    open(ROOT + name, "w").write(absolutize(doc))

# sitemap + robots + web manifest
urls = ["", "works", "about", "commission", "contact", "privacy", "terms"] + [f"works/{r[0]}" for r in order]
open(ROOT + "sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(ROOT + "robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
open(ROOT + "site.webmanifest", "w").write(json.dumps({
    "name": "John Akande", "short_name": "John Akande", "start_url": "/", "display": "browser",
    "background_color": "#f3eee4", "theme_color": "#f3eee4",
    "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2) + "\n")
print("ok", n_total, n_avail, n_sold, "pages", len(pages))

# vercel.json: clean URLs, HTTPS only, and security headers. The script hash lets only this
# site's own inline script run; it is recomputed here so it always matches the pages.
import base64, glob, hashlib
inline = set()
for f in glob.glob(ROOT + "*.html") + glob.glob(ROOT + "works/*.html"):
    for m in re.finditer(r'<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>(.*?)</script>', open(f).read(), re.S):
        inline.add(m.group(1))
hashes = " ".join(sorted("'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'" for s in inline))
CSP = "; ".join([
    "default-src 'self'",
    f"script-src 'self' {hashes}",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://api.fontshare.com",
    "font-src 'self' https://fonts.gstatic.com https://cdn.fontshare.com",
    "img-src 'self' data:",
    "media-src 'self'",
    "connect-src 'self' https://open.er-api.com",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests",
])
vercel = {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "cleanUrls": True,
    "trailingSlash": False,
    "headers": [{"source": "/(.*)", "headers": [
        {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains"},
        {"key": "Content-Security-Policy", "value": CSP},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=()"},
        {"key": "Cross-Origin-Opener-Policy", "value": "same-origin"},
    ]}],
}
with open(ROOT + "vercel.json", "w") as f:
    json.dump(vercel, f, indent=2)
    f.write("\n")
