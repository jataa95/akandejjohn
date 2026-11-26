(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

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
        if (btn.dataset.enquire) lbEnquire.href = `contact.html?work=${encodeURIComponent(btn.dataset.enquire)}`;
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
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = compose();
      let copied = false;
      try { await navigator.clipboard.writeText(text); copied = true; } catch {}
      window.open("https://ig.me/m/akandejjohn", "_blank", "noopener");
      status.textContent = copied
        ? "Message copied. Paste it into the Instagram chat that just opened."
        : "Copy the message above, then paste it into the Instagram chat.";
    });
  }
  // Artist statement: words light up as the quote scrolls through the screen
  $$("[data-words]").forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = "";
    const spans = words.map((w, i) => {
      const s = document.createElement("span");
      s.className = "w"; s.textContent = w;
      el.append(s, i < words.length - 1 ? " " : "");
      return s;
    });
    if (reduce) { spans.forEach((s) => s.classList.add("is-lit")); return; }
    const light = () => {
      const r = el.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35)));
      const n = Math.round(p * spans.length);
      spans.forEach((s, i) => s.classList.toggle("is-lit", i < n));
    };
    light(); addEventListener("scroll", light, { passive: true }); addEventListener("resize", light);
  });

  // Call to action: slow zoom-out of the background once on screen
  const cta = $(".cta");
  if (cta && "IntersectionObserver" in window) {
    const cio = new IntersectionObserver(([e]) => { if (e.isIntersecting) { cta.classList.add("is-in"); cio.disconnect(); } }, { threshold: 0.2 });
    cio.observe(cta);
  }

  // Selected works: horizontal gallery
  const hs = $("[data-hs]");
  if (hs) {
    const viewport = $("[data-hs-viewport]", hs), track = $("[data-hs-track]", hs);
    const bar = $("[data-hs-bar]", hs), idx = $("[data-hs-index]", hs);
    const prev = $("[data-hs-prev]", hs), next = $("[data-hs-next]", hs);
    const items = $$(".hs__item", hs);
    const pinnedMQ = matchMedia("(min-width: 861px)");
    let pinned = false, distance = 0, x = 0;
    const padL = () => parseFloat(getComputedStyle(viewport).paddingLeft) || 0;

    const setUI = (p) => {
      bar.style.width = `${(p * 100).toFixed(2)}%`;
      // the current work is the last one whose left edge has reached the gallery's left margin
      const left = viewport.getBoundingClientRect().left + padL() + 40;
      let cur = 0;
      items.forEach((it, i) => { if (it.getBoundingClientRect().left <= left) cur = i; });
      if (p >= 0.999) cur = items.length - 1;
      idx.textContent = String(cur + 1).padStart(2, "0");
      prev.disabled = p <= 0.001;
      next.disabled = p >= 0.999;
    };
    const update = () => {
      if (pinned) {
        const top = hs.getBoundingClientRect().top;
        const p = distance ? Math.min(1, Math.max(0, -top / distance)) : 0;
        x = p * distance;
        track.style.transform = `translate3d(${-x}px,0,0)`;
        setUI(p);
      } else {
        const max = viewport.scrollWidth - viewport.clientWidth;
        setUI(max > 0 ? viewport.scrollLeft / max : 0);
      }
    };
    const measure = () => {
      pinned = pinnedMQ.matches && !reduce;
      hs.classList.toggle("is-pinned", pinned);
      track.style.transform = "";
      hs.style.height = "";
      if (pinned) {
        distance = Math.max(0, track.scrollWidth - (viewport.clientWidth - padL() * 2));
        hs.style.height = `${innerHeight + distance}px`;
      }
      update();
    };
    // step one work left or right
    const step = (dir) => {
      const left = viewport.getBoundingClientRect().left + padL();
      const offsets = items.map((it) => it.getBoundingClientRect().left - left);
      const target = dir > 0 ? offsets.find((o) => o > 8) : [...offsets].reverse().find((o) => o < -8);
      if (pinned) {
        const goal = target === undefined ? (dir > 0 ? distance : 0) : Math.min(distance, Math.max(0, x + target));
        scrollTo({ top: hs.offsetTop + goal, behavior: "smooth" });
      } else {
        viewport.scrollBy({ left: target === undefined ? dir * viewport.clientWidth : target, behavior: "smooth" });
      }
    };
    prev.addEventListener("click", () => step(-1));
    next.addEventListener("click", () => step(1));

    // drag to scroll with a mouse when the gallery is not pinned
    let drag = null;
    viewport.addEventListener("pointerdown", (e) => {
      if (pinned || e.pointerType !== "mouse") return;
      drag = { x: e.clientX, l: viewport.scrollLeft, moved: false };
    });
    addEventListener("pointermove", (e) => {
      if (!drag) return;
      const dx = e.clientX - drag.x;
      if (Math.abs(dx) > 4) { drag.moved = true; viewport.classList.add("is-dragging"); }
      viewport.scrollLeft = drag.l - dx;
    });
    addEventListener("pointerup", () => {
      if (!drag) return;
      const moved = drag.moved;
      drag = null;
      viewport.classList.remove("is-dragging");
      if (moved) viewport.addEventListener("click", (e) => e.stopPropagation(), { capture: true, once: true });
    });

    viewport.addEventListener("scroll", () => { if (!pinned) update(); }, { passive: true });
    addEventListener("scroll", () => { if (pinned) requestAnimationFrame(update); }, { passive: true });
    addEventListener("resize", measure);
    addEventListener("load", measure);
    measure();
  }
})();
