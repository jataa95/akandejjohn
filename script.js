(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Intro monogram plays once per browser session
  try { sessionStorage.setItem("ja-intro", "1"); } catch {}

  // Year + Lagos clock (every [data-clock] on the page)
  $$("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));
  const clocks = $$("[data-clock]");
  const fmt = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", hour12: true, timeZone: "Africa/Lagos" });
  const tick = () => { const t = fmt.format(new Date()).toUpperCase(); clocks.forEach((c) => (c.textContent = t)); };
  tick(); setInterval(tick, 30000);

  // Navigation: frosted bar once scrolled
  const nav = $("[data-nav]");
  const onScroll = () => nav?.classList.toggle("is-scrolled", window.scrollY > 30);
  onScroll(); addEventListener("scroll", onScroll, { passive: true });
  if (nav) setTimeout(() => nav.classList.add("is-ready"), 300);

  // Full-screen menu
  const toggle = $("[data-menu-toggle]"), menu = $("[data-menu]");
  if (toggle && menu) {
    const label = $(".nav__toggle-label", toggle);
    const setOpen = (open) => {
      document.body.classList.toggle("menu-open", open);
      toggle.setAttribute("aria-expanded", open);
      label.textContent = open ? "Close" : "Menu";
    };
    toggle.addEventListener("click", () => setOpen(!document.body.classList.contains("menu-open")));
    $$("a", menu).forEach((a) => a.addEventListener("click", () => setOpen(false)));
    addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
    addEventListener("resize", () => { if (innerWidth > 860) setOpen(false); });
  }

  // Split hero name into letters
  $$("[data-split]").forEach((el) => {
    const text = el.textContent;
    el.textContent = "";
    [...text].forEach((c, i) => {
      const s = document.createElement("span");
      s.className = "ch";
      s.textContent = c === " " ? "\u00a0" : c;
      s.style.transitionDelay = `${i * 45}ms`;
      el.appendChild(s);
    });
    requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add("is-in")));
  });
  const heroMedia = $("[data-hero-media]");
  const stage = $("[data-parallax]");
  if (heroMedia) setTimeout(() => { heroMedia.classList.add("is-in"); stage?.classList.add("is-in"); }, 450);

  // Parallax: each floating image drifts at its own data-speed while the hero is on screen
  const floats = $$("[data-speed]");
  if (stage && floats.length && !reduce) {
    let ticking = false;
    const update = () => {
      ticking = false;
      const rect = stage.getBoundingClientRect();
      if (rect.bottom < -200 || rect.top > innerHeight + 200) return;
      const offset = -scrollY * (innerWidth < 760 ? 0.6 : 1); // 0 at the top of the page, so images start where the CSS puts them
      floats.forEach((el) => el.style.setProperty("--y", `${(offset * +el.dataset.speed).toFixed(1)}px`));
    };
    const req = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    update();
    addEventListener("scroll", req, { passive: true });
    addEventListener("resize", req);
  }
  // Pause the hero loop when it's off screen
  const heroVid = $(".hero__video");
  if (heroVid && "IntersectionObserver" in window) {
    new IntersectionObserver(([e]) => { e.isIntersecting ? heroVid.play().catch(() => {}) : heroVid.pause(); }).observe(heroVid);
  }

  // Reveal on scroll
  const items = $$(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach((e, i) => {
        e.target.style.transitionDelay = `${Math.min(i, 5) * 80}ms`;
        e.target.classList.add("is-in");
        io.unobserve(e.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    items.forEach((el) => io.observe(el));
  } else items.forEach((el) => el.classList.add("is-in"));

  // Counters
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const countIO = new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach(({ target }) => {
        countIO.unobserve(target);
        const end = +target.dataset.count, suffix = target.dataset.suffix || "";
        const t0 = performance.now(), dur = reduce ? 0 : 1600;
        const step = (t) => {
          const p = dur ? Math.min(1, (t - t0) / dur) : 1, v = Math.round(end * (1 - Math.pow(1 - p, 3)));
          target.innerHTML = v + suffix;
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    }, { threshold: 0.5 });
    counters.forEach((c) => countIO.observe(c));
  }

  // Studio film
  const story = $("[data-story]"), play = $("[data-play]");
  if (story && play) {
    const phone = story.closest(".phone");
    play.addEventListener("click", () => { story.controls = true; story.play(); });
    story.addEventListener("play", () => phone.classList.add("is-playing"));
    story.addEventListener("ended", () => { phone.classList.remove("is-playing"); story.controls = false; });
  }

  // Lightbox
  const dialog = $("[data-lightbox-dialog]");
  if (dialog) {
    const lbImg = $("[data-lb-img]", dialog), lbTitle = $("[data-lb-title]", dialog);
    const lbMeta = $("[data-lb-meta]", dialog), lbNote = $("[data-lb-note]", dialog);
    const lbEnquire = $("[data-lb-enquire]", dialog);
    $$("[data-lightbox]").forEach((btn) => btn.addEventListener("click", () => {
      lbImg.src = btn.dataset.src;
      lbImg.alt = $("img", btn)?.alt || "";
      lbTitle.textContent = btn.dataset.title;
      lbMeta.textContent = btn.dataset.meta || "";
      lbNote.textContent = btn.dataset.note || "";
      if (lbEnquire) {
        lbEnquire.hidden = !btn.dataset.enquire;
        if (btn.dataset.enquire) lbEnquire.href = `/contact?work=${encodeURIComponent(btn.dataset.enquire)}`;
      }
      dialog.showModal();
    }));
    $("[data-lightbox-close]", dialog).addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (e) => { if (e.target === dialog || e.target.tagName === "FIGURE") dialog.close(); });
  }

  // Works filters
  const grid = $("[data-works]");
  const chips = $$("[data-filter]");
  if (grid && chips.length) {
    chips.forEach((chip) => chip.addEventListener("click", () => {
      const f = chip.dataset.filter;
      chips.forEach((c) => c.setAttribute("aria-pressed", c === chip));
      $$(".work", grid).forEach((w) => {
        w.classList.toggle("is-hidden", f !== "all" && w.dataset.status !== f);
        w.classList.add("is-in");
      });
    }));
  }

  // Enquiry composer: build the message, copy it, open the Instagram chat
  const form = $("[data-composer]");
  if (form) {
    const preview = $("[data-preview]", form), status = $("[data-status]", form);
    const workField = $("[data-work-field]", form);
    const F = form.elements;
    const labels = { acquisition: "acquiring", commission: "a commission", exhibition: "an exhibition or press feature", live: "live painting" };
    const params = new URLSearchParams(location.search);
    const wantedType = params.get("type");
    if (wantedType) {
      const radio = [...F.type].find((r) => r.value === wantedType);
      if (radio) radio.checked = true;
    }
    const wanted = params.get("work");
    if (wanted) {
      const opt = [...F.work.options].find((o) => o.text === wanted);
      if (opt) opt.selected = true;
    }
    const compose = () => {
      const type = F.type.value;
      workField.hidden = type !== "acquisition";
      const name = F.name.value.trim(), work = F.work.value, msg = F.message.value.trim();
      let subject = labels[type];
      if (type === "acquisition") subject = work ? `acquiring “${work}”` : "acquiring one of your paintings";
      const lines = [`Hello John,${name ? ` I'm ${name}.` : ""} I'd like to enquire about ${subject}.`];
      if (msg) lines.push("", msg);
      lines.push("", "(Sent from akandejjohn website)");
      return lines.join("\n");
    };
    const render = () => { preview.textContent = compose(); };
    form.addEventListener("input", render);
    form.addEventListener("change", render);
    render();
    // Send: opens the visitor's email app with the enquiry addressed to John, ready to send
    const subjects = { acquisition: "Acquisition enquiry", commission: "Commission enquiry", exhibition: "Exhibition / press enquiry", live: "Live painting enquiry" };
    const nameErr = $("[data-error-for=name]", form);
    const validName = () => F.name.value.trim().length >= 2;
    const showNameError = (show) => {
      nameErr.hidden = !show;
      F.name.setAttribute("aria-invalid", show ? "true" : "false");
    };
    F.name.addEventListener("input", () => { if (!nameErr.hidden && validName()) showNameError(false); });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!validName()) { showNameError(true); F.name.focus(); return; }
      const email = form.dataset.email;
      const type = F.type.value, work = F.work.value;
      const subject = subjects[type] + (type === "acquisition" && work ? `: ${work}` : "");
      location.href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(compose())}`;
      status.innerHTML = "";
      status.append(`Your email app should open with the message ready to send. If it doesn’t, email John at `);
      const a = document.createElement("a"); a.href = `mailto:${email}`; a.className = "link"; a.textContent = email;
      status.append(a, ".");
    });
  }
  // Call to action: slow zoom-out of the background once on screen
  const cta = $(".cta");
  if (cta && "IntersectionObserver" in window) {
    const cio = new IntersectionObserver(([e]) => { if (e.isIntersecting) { cta.classList.add("is-in"); cio.disconnect(); } }, { threshold: 0.2 });
    cio.observe(cta);
  }

  // Selected works: hovering or focusing a row shows that painting in the preview
  const sel = $("[data-sel-root]");
  if (sel) {
    const rows = $$("[data-sel]", sel), imgs = $$("[data-sel-img]", sel);
    const idx = $("[data-sel-index]", sel), title = $("[data-sel-title]", sel), size = $("[data-sel-size]", sel);
    let active = 0;
    const show = (i) => {
      if (i === active) return;
      active = i;
      imgs.forEach((im) => im.classList.toggle("is-active", +im.dataset.selImg === i));
      rows.forEach((r) => r.classList.toggle("is-active", +r.dataset.sel === i));
      const row = rows[i];
      idx.textContent = String(i + 1).padStart(2, "0");
      title.textContent = row.dataset.title;
      size.textContent = `${$(".sel__size", row).textContent} · Acrylic on canvas`;
    };
    rows[0]?.classList.add("is-active");
    rows.forEach((r) => {
      const i = +r.dataset.sel;
      r.addEventListener("mouseenter", () => show(i));
      r.addEventListener("focus", () => show(i));
    });
  }

  // Currency: prices are set in US dollars; other currencies are converted at the day's rate
  const priced = $$("[data-usd]");
  if (priced.length) {
    const CURRENCIES = {
      USD: { locale: "en-US", round: 1 },
      EUR: { locale: "en-IE", round: 10 },
      GBP: { locale: "en-GB", round: 10 },
      NGN: { locale: "en-NG", round: 1000 },
    };
    // used only if the live rates can't be loaded; approximate
    const FALLBACK = { USD: 1, EUR: 0.87, GBP: 0.76, NGN: 1500 };
    const RATES_KEY = "akande-rates", CUR_KEY = "akande-currency";
    const store = {
      get(k) { try { return localStorage.getItem(k); } catch { return null; } },
      set(k, v) { try { localStorage.setItem(k, v); } catch {} },
    };
    let rates = null, live = false;
    try {
      const cached = JSON.parse(store.get(RATES_KEY) || "null");
      if (cached && Date.now() - cached.t < 12 * 3600e3) { rates = cached.r; live = true; }
    } catch {}
    let current = store.get(CUR_KEY);
    if (!CURRENCIES[current]) current = "USD";

    const sw = $("[data-currency-switch]");
    const note = $("[data-currency-note]");
    const format = (usd, cur) => {
      const c = CURRENCIES[cur];
      const rate = (rates || FALLBACK)[cur] || FALLBACK[cur];
      const value = Math.round((usd * rate) / c.round) * c.round;
      const text = new Intl.NumberFormat(c.locale, { style: "currency", currency: cur, maximumFractionDigits: 0 }).format(value);
      return cur === "USD" ? text : `≈ ${text}`;
    };
    const apply = (cur) => {
      current = cur;
      priced.forEach((el) => {
        const text = format(+el.dataset.usd, cur);
        if (el.matches("[data-lightbox]")) el.dataset.meta = `${el.dataset.size} · Acrylic on canvas · ${text}`;
        else el.textContent = text;
      });
      if (sw) $$("[data-currency]", sw).forEach((b) => b.setAttribute("aria-pressed", b.dataset.currency === cur));
      if (note) {
        note.textContent = cur === "USD"
          ? "Prices are set in US dollars."
          : `Approximate, converted from US dollars at ${live ? "today’s" : "a recent"} rate. Final price is agreed in US dollars.`;
      }
    };
    if (sw) sw.addEventListener("click", (e) => {
      const b = e.target.closest("[data-currency]");
      if (!b) return;
      store.set(CUR_KEY, b.dataset.currency);
      apply(b.dataset.currency);
    });
    apply(current);

    if (!live && (sw || current !== "USD")) {
      fetch("https://open.er-api.com/v6/latest/USD")
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((d) => {
          if (d && d.rates && d.rates.EUR && d.rates.GBP && d.rates.NGN) {
            rates = { USD: 1, EUR: d.rates.EUR, GBP: d.rates.GBP, NGN: d.rates.NGN };
            live = true;
            store.set(RATES_KEY, JSON.stringify({ t: Date.now(), r: rates }));
            apply(current);
          }
        })
        .catch(() => {});
    }
  }
  // Hero: mute / unmute plays the film's soundtrack (normal speed) over the muted loop
  const muteBtn = $("[data-hero-mute]"), heroAudio = $("[data-hero-audio]");
  if (muteBtn && heroAudio) {
    let wantSound = false;
    const setUI = (on) => {
      muteBtn.setAttribute("aria-pressed", on);
      muteBtn.setAttribute("aria-label", on ? "Mute" : "Unmute");
    };
    muteBtn.addEventListener("click", () => {
      wantSound = !wantSound;
      if (wantSound) heroAudio.play().then(() => setUI(true)).catch(() => { wantSound = false; setUI(false); });
      else { heroAudio.pause(); setUI(false); }
    });
    // pause the sound while the hero is off screen or the tab is hidden, resume when it is back
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => {
        if (!wantSound) return;
        e.isIntersecting ? heroAudio.play().catch(() => {}) : heroAudio.pause();
      }, { threshold: 0.15 }).observe(muteBtn.closest(".hero__media"));
    }
    document.addEventListener("visibilitychange", () => { if (document.hidden) heroAudio.pause(); else if (wantSound) heroAudio.play().catch(() => {}); });
  }
  // Payment details: copy account numbers
  $$("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    const value = btn.parentElement.querySelector("[data-copy-value]")?.textContent.trim();
    if (!value) return;
    try { await navigator.clipboard.writeText(value); } catch { return; }
    btn.textContent = "Copied"; btn.classList.add("is-done");
    setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("is-done"); }, 1800);
  }));
})();
