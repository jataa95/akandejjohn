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
    addEventListener("resize", () => { if (innerWidth > 960) setOpen(false); });
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
    const wanted = new URLSearchParams(location.search).get("work");
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
})();
