/* =========================================================================
   Fundación Reserva para la Infancia — main.js
   Sin dependencias externas. Progressive enhancement + accesibilidad.
   ========================================================================= */
(function () {
  'use strict';

  document.documentElement.classList.remove('no-js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. Tema claro / oscuro ---------- */
  function initTheme() {
    var btn = document.querySelector('.theme-btn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      btn.setAttribute('aria-label', next === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro');
      try { localStorage.setItem('fri-theme', next); } catch (e) {}
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
      toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
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

    function run(el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var suffix = el.getAttribute('data-suffix') || '';
      if (reduceMotion) { el.textContent = target + suffix; return; }
      var start = performance.now(), dur = 1600;
      function frame(now) {
        var p = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString('es-CO') + suffix;
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
    box.setAttribute('aria-label', 'Galería ampliada');
    box.innerHTML =
      '<button class="lightbox__close" aria-label="Cerrar galería"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg></button>' +
      '<button class="lightbox__nav lightbox__nav--prev" aria-label="Imagen anterior"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg></button>' +
      '<button class="lightbox__nav lightbox__nav--next" aria-label="Imagen siguiente"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg></button>' +
      '<figure><div class="lightbox__stage"></div><figcaption></figcaption></figure>';
    document.body.appendChild(box);

    var stage = box.querySelector('.lightbox__stage');
    var caption = box.querySelector('figcaption');
    var index = 0, lastFocus = null;

    function render(i) {
      var visible = items.filter(function (it) { return !it.classList.contains('is-hidden'); });
      if (!visible.length) return;
      index = (i + visible.length) % visible.length;
      var src = visible[index];
      var media = src.querySelector('img, svg');
      stage.innerHTML = '';
      if (media) stage.appendChild(media.cloneNode(true));
      var cap = src.querySelector('figcaption');
      caption.textContent = cap ? cap.textContent : '';
      box.dataset.visibleCount = visible.length;
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
      function openThis() {
        var visible = items.filter(function (it) { return !it.classList.contains('is-hidden'); });
        open(visible.indexOf(item));
      }
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

  /* ---------- 10. Validación de formularios ---------- */
  function initForms() {
    document.querySelectorAll('form[data-validate]').forEach(function (form) {
      var status = form.querySelector('.form-status');

      function validateField(input) {
        var field = input.closest('.field') || input.closest('.check');
        if (!field) return true;
        var ok = input.checkValidity();
        field.classList.toggle('is-invalid', !ok);
        return ok;
      }

      form.querySelectorAll('input, select, textarea').forEach(function (input) {
        input.addEventListener('blur', function () { validateField(input); });
        input.addEventListener('input', function () {
          var field = input.closest('.field');
          if (field && field.classList.contains('is-invalid')) validateField(input);
        });
      });

      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var valid = true, firstBad = null;
        form.querySelectorAll('input, select, textarea').forEach(function (input) {
          if (!validateField(input)) { valid = false; if (!firstBad) firstBad = input; }
        });
        if (!valid) { if (firstBad) firstBad.focus(); return; }

        var btn = form.querySelector('button[type="submit"]');
        var original = btn ? btn.textContent : '';
        if (btn) { btn.disabled = true; btn.textContent = 'Enviando…'; }

        // Demo local: sin backend, se simula el envío.
        // Para producción, reemplazar por fetch() al endpoint real (ver README.md).
        setTimeout(function () {
          if (btn) { btn.disabled = false; btn.textContent = original; }
          if (status) {
            status.textContent = form.getAttribute('data-success') ||
              '¡Gracias! Hemos recibido tu mensaje. Te responderemos en un plazo máximo de 2 días hábiles.';
            status.classList.add('is-visible');
            status.setAttribute('role', 'status');
            status.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
          }
          form.reset();
        }, 900);
      });
    });
  }

  /* ---------- 11. Buscador interno ---------- */
  var SEARCH_INDEX = [
    { t: 'Inicio', d: 'Colegio de pedagogía viva en Barichara, Santander.', u: 'index.html' },
    { t: 'Quiénes somos', d: 'Historia, misión, visión, valores y equipo directivo.', u: 'nosotros.html' },
    { t: 'Historia · 25 años', d: 'De la reserva natural al colegio: nuestra línea de tiempo.', u: 'nosotros.html#historia' },
    { t: 'Misión y visión', d: 'Nuestro horizonte institucional.', u: 'nosotros.html#horizonte' },
    { t: 'Equipo', d: 'Rectoría, coordinación y acompañantes.', u: 'nosotros.html#equipo' },
    { t: 'Proyecto educativo (PEI)', d: 'Pedagogía viva, aprendizaje en la naturaleza y evaluación por procesos.', u: 'proyecto-educativo.html' },
    { t: 'Pedagogía viva', d: 'Qué es y cómo la practicamos día a día.', u: 'proyecto-educativo.html#pedagogia' },
    { t: 'Ambientes de aprendizaje', d: 'Huerta, bosque, taller, biblioteca y aulas abiertas.', u: 'proyecto-educativo.html#ambientes' },
    { t: 'Niveles educativos', d: 'Preescolar, primaria, secundaria y media.', u: 'niveles.html' },
    { t: 'Preescolar', d: 'Pre-jardín, jardín I y jardín II.', u: 'niveles.html#preescolar' },
    { t: 'Básica primaria', d: 'Grados 1º a 5º.', u: 'niveles.html#primaria' },
    { t: 'Básica secundaria', d: 'Grados 6º a 9º.', u: 'niveles.html#secundaria' },
    { t: 'Educación media', d: 'Grados 10º y 11º, con resultados Saber 11 sobre el promedio nacional.', u: 'niveles.html#media' },
    { t: 'Vida escolar', d: 'Arte, huerta, deporte, campamentos y campus.', u: 'vida-escolar.html' },
    { t: 'Campus y reserva', d: 'Cuatro hectáreas en la vereda El Llano.', u: 'vida-escolar.html#campus' },
    { t: 'Galería', d: 'Fotografías de la vida cotidiana del colegio.', u: 'vida-escolar.html#galeria' },
    { t: 'Calendario escolar', d: 'Fechas clave del calendario A.', u: 'vida-escolar.html#calendario' },
    { t: 'Admisiones', d: 'Proceso de ingreso paso a paso, requisitos y costos.', u: 'admisiones.html' },
    { t: 'Proceso de admisión', d: 'Cinco pasos, desde la solicitud hasta la matrícula.', u: 'admisiones.html#proceso' },
    { t: 'Requisitos y documentos', d: 'Qué necesitas para inscribirte.', u: 'admisiones.html#requisitos' },
    { t: 'Costos educativos', d: 'Matrícula, pensión y becas.', u: 'admisiones.html#costos' },
    { t: 'Preguntas frecuentes', d: 'Transporte, alimentación, uniformes y más.', u: 'admisiones.html#faq' },
    { t: 'Formulario de admisión', d: 'Solicita tu cupo en línea.', u: 'admisiones.html#formulario' },
    { t: 'Noticias y agenda', d: 'Novedades, comunicados y circulares.', u: 'noticias.html' },
    { t: 'Contacto', d: 'Teléfonos, correo, mapa y formulario.', u: 'contacto.html' },
    { t: 'Cómo llegar', d: 'Vía Barichara – San Gil, km 4, vereda El Llano.', u: 'contacto.html#mapa' }
  ];

  function initSearch() {
    var openers = document.querySelectorAll('[data-open-search]');
    if (!openers.length) return;

    var dlg = document.createElement('div');
    dlg.className = 'search-dialog';
    dlg.setAttribute('role', 'dialog');
    dlg.setAttribute('aria-modal', 'true');
    dlg.setAttribute('aria-label', 'Buscar en el sitio');
    dlg.innerHTML =
      '<div class="search-box">' +
      '<input type="search" placeholder="Buscar: admisiones, pedagogía, costos…" aria-label="Buscar en el sitio" autocomplete="off">' +
      '<div class="search-results" role="listbox"></div></div>';
    document.body.appendChild(dlg);

    var input = dlg.querySelector('input');
    var out = dlg.querySelector('.search-results');
    var lastFocus = null;

    function norm(s) {
      return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }
    function render(q) {
      var query = norm(q.trim());
      var list = query.length < 2
        ? SEARCH_INDEX.slice(0, 6)
        : SEARCH_INDEX.filter(function (i) { return norm(i.t + ' ' + i.d).indexOf(query) !== -1; });
      if (!list.length) {
        out.innerHTML = '<p class="search-empty">Sin resultados para “' + q.replace(/</g, '&lt;') + '”. Prueba con «admisiones» o «pedagogía».</p>';
        return;
      }
      out.innerHTML = list.slice(0, 8).map(function (i) {
        return '<a href="' + i.u + '"><b>' + i.t + '</b><span>' + i.d + '</span></a>';
      }).join('');
    }
    function open() {
      lastFocus = document.activeElement;
      dlg.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      render('');
      input.value = '';
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
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); dlg.classList.contains('is-open') ? close() : open(); }
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
      if (!target) return;
      if (target.split('#')[0] === here) a.setAttribute('aria-current', 'page');
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
        navigator.serviceWorker.register('sw.js').catch(function () {});
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
