(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Year + Lagos clock
  const year = $("[data-year]");
  if (year) year.textContent = new Date().getFullYear();
  const clock = $("[data-clock]");
  const tick = () => {
    if (!clock) return;
    clock.textContent = new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit", minute: "2-digit", hour12: true, timeZone: "Africa/Lagos",
    }).format(new Date()).toUpperCase();
  };
  tick(); setInterval(tick, 30000);

  // Top bar background
  const bar = $("[data-bar]");
  const onScroll = () => bar.classList.toggle("is-scrolled", window.scrollY > 40);
  onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

  // Split hero name into letters
  $$("[data-split]").forEach((el) => {
    const text = el.textContent;
    el.textContent = "";
    [...text].forEach((c, i) => {
      const s = document.createElement("span");
      s.className = "ch";
      s.textContent = c === " " ? " " : c;
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
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
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
        e.target.style.transitionDelay = `${i * 80}ms`;
        e.target.classList.add("is-in");
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    items.forEach((el) => io.observe(el));
  } else items.forEach((el) => el.classList.add("is-in"));

  // Counters
  const counters = $$("[data-count]");
  const countIO = new IntersectionObserver((entries) => {
    entries.filter((e) => e.isIntersecting).forEach(({ target }) => {
      countIO.unobserve(target);
      const end = +target.dataset.count, suffix = target.dataset.suffix || "";
      const t0 = performance.now(), dur = 1600;
      const step = (t) => {
        const p = Math.min(1, (t - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - p, 3)));
        target.innerHTML = v + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.5 });
  counters.forEach((c) => countIO.observe(c));

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
  const lbImg = $("[data-lb-img]", dialog), lbTitle = $("[data-lb-title]", dialog);
  const lbMeta = $("[data-lb-meta]", dialog), lbNote = $("[data-lb-note]", dialog);
  $$("[data-lightbox]").forEach((btn) => btn.addEventListener("click", () => {
    lbImg.src = btn.dataset.src;
    lbImg.alt = $("img", btn)?.alt || "";
    lbTitle.textContent = btn.dataset.title;
    lbMeta.textContent = btn.dataset.meta || "";
    lbNote.textContent = btn.dataset.note || "";
    dialog.showModal();
  }));
  $("[data-lightbox-close]", dialog).addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => { if (e.target === dialog || e.target.tagName === "FIGURE") dialog.close(); });
})();
