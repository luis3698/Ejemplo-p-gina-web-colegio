/* =========================================================================
   Sitio web escolar — main.js
   Sin dependencias externas. Progressive enhancement + accesibilidad.
   Los textos y el índice de búsqueda llegan por idioma en window.SITE_I18N,
   que inyecta tools/build.py en cada página.
   ========================================================================= */
(function () {
  'use strict';

  document.documentElement.classList.remove('no-js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var T = window.SITE_I18N || {};
  var STRINGS = {
    searchPlaceholder: T.searchPlaceholder || 'Buscar…',
    searchAria: T.searchAria || 'Buscar en el sitio',
    searchEmpty: T.searchEmpty || 'Sin resultados para “{q}”.',
    sending: T.sending || 'Enviando…',
    formError: T.formError || 'No pudimos enviar el mensaje. Inténtalo de nuevo.',
    formDemo: T.formDemo || 'Modo demostración: no hay destinatario configurado.',
    closeMenu: T.closeMenu || 'Cerrar menú',
    openMenu: T.openMenu || 'Abrir menú',
    themeLight: T.themeLight || 'Cambiar a tema claro',
    themeDark: T.themeDark || 'Cambiar a tema oscuro'
  };

  /* ---------- 1. Tema claro / oscuro ---------- */
  function initTheme() {
    var btn = document.querySelector('.theme-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      btn.setAttribute('aria-label', next === 'dark' ? STRINGS.themeLight : STRINGS.themeDark);
      try { localStorage.setItem('site-theme', next); } catch (e) {}
    });
  }

  /* ---------- 2. Menú móvil ---------- */
  function initNav() {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.nav');
    if (!toggle || !nav) return;

    function setOpen(open) {
      nav.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? STRINGS.closeMenu : STRINGS.openMenu);
    }
    toggle.addEventListener('click', function () {
      setOpen(!nav.classList.contains('is-open'));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 920 && nav.classList.contains('is-open')) setOpen(false);
    });
  }

  /* ---------- 3. Cabecera fija + progreso de lectura ---------- */
  function initScrollUI() {
    var header = document.querySelector('.header');
    var bar = document.querySelector('.progress');
    var top = document.querySelector('.to-top');
    var ticking = false;

    function update() {
      var y = window.scrollY || document.documentElement.scrollTop;
      if (header) header.classList.toggle('is-stuck', y > 8);
      if (top) top.classList.toggle('is-visible', y > 600);
      if (bar) {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
      }
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();

    if (top) top.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- 4. Aparición al hacer scroll ---------- */
  function initReveal() {
    var items = document.querySelectorAll('[data-reveal]');
    if (!items.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 5. Contadores animados ---------- */
  function initCounters() {
    var nums = document.querySelectorAll('[data-count]');
    if (!nums.length) return;
    var locale = document.documentElement.lang || 'es-CO';

    function run(el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var suffix = el.getAttribute('data-suffix') || '';
      if (reduceMotion) { el.textContent = target + suffix; return; }
      var start = performance.now(), dur = 1600;
      function frame(now) {
        var p = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString(locale) + suffix;
        if (p < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
    if (!('IntersectionObserver' in window)) { nums.forEach(run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 6. Acordeón accesible ---------- */
  function initAccordion() {
    document.querySelectorAll('.acc__btn').forEach(function (btn) {
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (!panel) return;
      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';
        var group = btn.closest('.accordion');
        if (group && !open) {
          group.querySelectorAll('.acc__btn[aria-expanded="true"]').forEach(function (other) {
            other.setAttribute('aria-expanded', 'false');
            var p = document.getElementById(other.getAttribute('aria-controls'));
            if (p) p.style.height = '0px';
          });
        }
        btn.setAttribute('aria-expanded', String(!open));
        panel.style.height = open ? '0px' : panel.scrollHeight + 'px';
      });
      panel.addEventListener('transitionend', function () {
        if (btn.getAttribute('aria-expanded') === 'true') panel.style.height = 'auto';
      });
    });
  }

  /* ---------- 7. Carrusel de testimonios ---------- */
  function initQuotes() {
    document.querySelectorAll('.quotes').forEach(function (root) {
      var track = root.querySelector('.quotes__track');
      var prev = root.querySelector('[data-q="prev"]');
      var next = root.querySelector('[data-q="next"]');
      if (!track) return;
      function step(dir) {
        var card = track.querySelector('.quote');
        var w = card ? card.offsetWidth + 24 : track.clientWidth;
        track.scrollBy({ left: dir * w, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
      if (prev) prev.addEventListener('click', function () { step(-1); });
      if (next) next.addEventListener('click', function () { step(1); });
    });
  }

  /* ---------- 8. Filtros (galería y noticias) ---------- */
  function initFilters() {
    document.querySelectorAll('[data-filter-group]').forEach(function (group) {
      var targetSel = group.getAttribute('data-filter-target');
      var items = document.querySelectorAll(targetSel);
      group.addEventListener('click', function (e) {
        var btn = e.target.closest('.filter');
        if (!btn) return;
        group.querySelectorAll('.filter').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
        btn.setAttribute('aria-pressed', 'true');
        var value = btn.getAttribute('data-filter');
        items.forEach(function (item) {
          var show = value === 'todos' || item.getAttribute('data-cat') === value;
          item.classList.toggle('is-hidden', !show);
        });
      });
    });
  }

  /* ---------- 9. Lightbox de galería ---------- */
  function initLightbox() {
    var items = Array.prototype.slice.call(document.querySelectorAll('.gallery__item'));
    if (!items.length) return;

    var box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML =
      '<button class="lightbox__close" aria-label="×"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg></button>' +
      '<button class="lightbox__nav lightbox__nav--prev" aria-label="‹"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg></button>' +
      '<button class="lightbox__nav lightbox__nav--next" aria-label="›"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg></button>' +
      '<figure><div class="lightbox__stage"></div><figcaption></figcaption></figure>';
    document.body.appendChild(box);

    var stage = box.querySelector('.lightbox__stage');
    var caption = box.querySelector('figcaption');
    var index = 0, lastFocus = null;

    function visibleItems() {
      return items.filter(function (it) { return !it.classList.contains('is-hidden'); });
    }
    function render(i) {
      var visible = visibleItems();
      if (!visible.length) return;
      index = (i + visible.length) % visible.length;
      var src = visible[index];
      var media = src.querySelector('picture, img, svg');
      stage.innerHTML = '';
      if (media) {
        var clone = media.cloneNode(true);
        clone.removeAttribute('style');       // quita el placeholder borroso
        var innerImg = clone.tagName === 'IMG' ? clone : clone.querySelector('img');
        if (innerImg) { innerImg.setAttribute('loading', 'eager'); innerImg.removeAttribute('sizes'); }
        stage.appendChild(clone);
      }
      var cap = src.querySelector('figcaption');
      caption.textContent = cap ? cap.textContent : '';
    }
    function open(i) {
      lastFocus = document.activeElement;
      render(i);
      box.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      box.querySelector('.lightbox__close').focus();
    }
    function close() {
      box.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }
    items.forEach(function (item) {
      function openThis() { open(visibleItems().indexOf(item)); }
      item.addEventListener('click', openThis);
      item.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); openThis(); }
      });
    });
    box.querySelector('.lightbox__close').addEventListener('click', close);
    box.querySelector('.lightbox__nav--prev').addEventListener('click', function () { render(index - 1); });
    box.querySelector('.lightbox__nav--next').addEventListener('click', function () { render(index + 1); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    document.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') render(index - 1);
      if (e.key === 'ArrowRight') render(index + 1);
    });
  }

  /* ---------- 10. Formularios: validación + envío real ---------- */
  /*  MEJORA 1.
      Si tools/build.py tiene configurado SITE['form_endpoint'], el formulario
      se envía de verdad por fetch() a ese endpoint (Formspree, Web3Forms,
      Getform o un backend propio). Si no, queda en modo demostración: valida
      y avisa con claridad que aún no hay destinatario.                       */
  function initForms() {
    var endpoint = T.formEndpoint && T.formEndpoint !== 'PENDIENTE' ? T.formEndpoint : null;

    document.querySelectorAll('form[data-validate]').forEach(function (form) {
      var status = form.querySelector('.form-status');

      if (endpoint) {
        form.setAttribute('action', endpoint);
        form.setAttribute('method', 'POST');
      }

      function say(message, isError) {
        if (!status) return;
        status.textContent = message;
        status.classList.add('is-visible');
        status.classList.toggle('form-status--error', !!isError);
        status.setAttribute('role', isError ? 'alert' : 'status');
        status.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
      }

      function validateField(input) {
        var field = input.closest('.field');
        if (!field) return input.checkValidity();
        var ok = input.checkValidity();
        field.classList.toggle('is-invalid', !ok);
        input.setAttribute('aria-invalid', ok ? 'false' : 'true');
        return ok;
      }

      form.querySelectorAll('input, select, textarea').forEach(function (input) {
        if (input.type === 'hidden') return;
        input.addEventListener('blur', function () { validateField(input); });
        input.addEventListener('input', function () {
          var field = input.closest('.field');
          if (field && field.classList.contains('is-invalid')) validateField(input);
        });
      });

      form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Trampa antispam: si un robot la rellena, fingimos éxito y no enviamos.
        var honey = form.querySelector('input[name="_gotcha"]');
        if (honey && honey.value) { say(form.getAttribute('data-success')); form.reset(); return; }

        var valid = true, firstBad = null;
        form.querySelectorAll('input, select, textarea').forEach(function (input) {
          if (input.type === 'hidden') return;
          if (!validateField(input)) { valid = false; if (!firstBad) firstBad = input; }
        });
        if (!valid) { if (firstBad) firstBad.focus(); return; }

        var btn = form.querySelector('button[type="submit"]');
        var original = btn ? btn.textContent : '';
        function restore() { if (btn) { btn.disabled = false; btn.textContent = original; } }
        if (btn) { btn.disabled = true; btn.textContent = STRINGS.sending; }

        if (!endpoint) {
          // Modo demostración.
          setTimeout(function () {
            restore();
            say(form.getAttribute('data-success') + ' — ' + STRINGS.formDemo);
            form.reset();
          }, 700);
          return;
        }

        var data = new FormData(form);
        if (T.formAccessKey) data.append('access_key', T.formAccessKey);
        data.append('_subject', form.getAttribute('data-subject') || document.title);
        data.append('_language', document.documentElement.lang || 'es');
        data.append('_page', location.href);

        fetch(endpoint, {
          method: 'POST',
          body: data,
          headers: { Accept: 'application/json' }
        })
          .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json().catch(function () { return {}; });
          })
          .then(function (json) {
            if (json && json.success === false) throw new Error(json.message || 'rejected');
            restore();
            say(form.getAttribute('data-success'));
            form.reset();
            form.querySelectorAll('.is-invalid').forEach(function (f) { f.classList.remove('is-invalid'); });
          })
          .catch(function () {
            restore();
            say(STRINGS.formError, true);
          });
      });
    });
  }

  /* ---------- 11. Buscador interno ---------- */
  function initSearch() {
    var openers = document.querySelectorAll('[data-open-search]');
    var index = T.search || [];
    if (!openers.length || !index.length) return;

    var dlg = document.createElement('div');
    dlg.className = 'search-dialog';
    dlg.setAttribute('role', 'dialog');
    dlg.setAttribute('aria-modal', 'true');
    dlg.setAttribute('aria-label', STRINGS.searchAria);
    dlg.innerHTML =
      '<div class="search-box">' +
      '<input type="search" autocomplete="off">' +
      '<div class="search-results"></div></div>';
    document.body.appendChild(dlg);

    var input = dlg.querySelector('input');
    input.placeholder = STRINGS.searchPlaceholder;
    input.setAttribute('aria-label', STRINGS.searchAria);
    var out = dlg.querySelector('.search-results');
    var lastFocus = null;

    function norm(s) {
      return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }
    function escape(s) {
      return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function render(q) {
      var query = norm(q.trim());
      var list = query.length < 2
        ? index.slice(0, 6)
        : index.filter(function (i) { return norm(i.t + ' ' + i.d).indexOf(query) !== -1; });
      if (!list.length) {
        out.innerHTML = '<p class="search-empty">' +
          escape(STRINGS.searchEmpty).replace('{q}', escape(q)) + '</p>';
        return;
      }
      out.innerHTML = list.slice(0, 8).map(function (i) {
        return '<a href="' + i.u + '"><b>' + escape(i.t) + '</b><span>' + escape(i.d) + '</span></a>';
      }).join('');
    }
    function open() {
      lastFocus = document.activeElement;
      dlg.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      input.value = '';
      render('');
      input.focus();
    }
    function close() {
      dlg.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }
    openers.forEach(function (b) { b.addEventListener('click', open); });
    input.addEventListener('input', function () { render(input.value); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && dlg.classList.contains('is-open')) close();
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (dlg.classList.contains('is-open')) { close(); } else { open(); }
      }
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); var f = out.querySelector('a'); if (f) f.focus(); }
      if (e.key === 'Enter') { var first = out.querySelector('a'); if (first) first.click(); }
    });
  }

  /* ---------- 12. Enlace activo en la navegación ---------- */
  function initActiveLink() {
    var here = location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav__link').forEach(function (a) {
      var target = a.getAttribute('href');
      if (target && target.split('#')[0] === here) a.setAttribute('aria-current', 'page');
    });
  }

  /* ---------- 13. Año actual en el pie ---------- */
  function initYear() {
    document.querySelectorAll('[data-year]').forEach(function (el) {
      el.textContent = new Date().getFullYear();
    });
  }

  /* ---------- Arranque ---------- */
  function boot() {
    initTheme(); initNav(); initScrollUI(); initReveal(); initCounters();
    initAccordion(); initQuotes(); initFilters(); initLightbox();
    initForms(); initSearch(); initActiveLink(); initYear();

    if ('serviceWorker' in navigator && location.protocol.indexOf('http') === 0) {
      window.addEventListener('load', function () {
        var base = document.documentElement.lang === 'en' ? '../sw.js' : 'sw.js';
        navigator.serviceWorker.register(base).catch(function () {});
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
