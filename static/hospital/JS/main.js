/**
 * MEDICORE — GLOBAL JAVASCRIPT
 * Scroll-reveal, counter animation, navbar scroll class,
 * theme toggle (dark mode), toast notifications, scroll progress
 */

(function () {
    'use strict';

    /* ---- 1. Scroll Reveal ---- */
    function initReveal() {
        const els = document.querySelectorAll('.reveal');
        if (!els.length) return;

        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        els.forEach(function (el) { io.observe(el); });
    }


    /* ---- 2. Count-up numbers ---- */
    function initCountUp() {
        const els = document.querySelectorAll('[data-count]');
        if (!els.length) return;

        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                io.unobserve(entry.target);

                var el      = entry.target;
                var target  = parseFloat(el.dataset.count);
                var suffix  = el.dataset.suffix || '';
                var prefix  = el.dataset.prefix || '';
                var dur     = 1600;
                var start   = performance.now();

                function step(now) {
                    var progress = Math.min((now - start) / dur, 1);
                    var eased    = 1 - Math.pow(1 - progress, 3);
                    var value    = Math.floor(eased * target);
                    el.textContent = prefix + value + suffix;
                    if (progress < 1) requestAnimationFrame(step);
                }

                requestAnimationFrame(step);
            });
        }, { threshold: 0.5 });

        els.forEach(function (el) { io.observe(el); });
    }


    /* ---- 3. Navbar scroll shadow ---- */
    function initNavbarScroll() {
        var navbar = document.querySelector('.navbar');
        if (!navbar) return;

        function onScroll() {
            navbar.classList.toggle('navbar--scrolled', window.scrollY > 8);
        }

        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }


    /* ---- 4. Smooth scroll for anchor links ---- */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (link) {
            link.addEventListener('click', function (e) {
                var id = link.getAttribute('href').slice(1);
                if (!id) return;
                var target = document.getElementById(id);
                if (!target) return;
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }


    /* ---- 5. Auto-dismiss messages ---- */
    function initAutoDismiss() {
        document.querySelectorAll('.alert, .auth-alert').forEach(function (el) {
            setTimeout(function () {
                el.style.transition = 'opacity 0.5s, transform 0.5s';
                el.style.opacity = '0';
                el.style.transform = 'translateY(-8px)';
                setTimeout(function () { el.remove(); }, 500);
            }, 4000);
        });
    }


    /* ---- 6. Dark Mode Theme Toggle ---- */
    function initThemeToggle() {
        var btn = document.getElementById('themeToggle');
        var html = document.documentElement;

        // Apply saved preference immediately (no flash)
        var saved = localStorage.getItem('medicore-theme');
        if (saved === 'dark') {
            html.setAttribute('data-theme', 'dark');
        }

        if (!btn) return;

        btn.addEventListener('click', function () {
            var current = html.getAttribute('data-theme');
            var next = current === 'dark' ? 'light' : 'dark';

            if (next === 'dark') {
                html.setAttribute('data-theme', 'dark');
                localStorage.setItem('medicore-theme', 'dark');
            } else {
                html.removeAttribute('data-theme');
                localStorage.setItem('medicore-theme', 'light');
            }

            // Announce to screen readers
            btn.setAttribute(
                'aria-label',
                next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
            );
        });

        // Set initial aria-label
        btn.setAttribute(
            'aria-label',
            html.getAttribute('data-theme') === 'dark'
                ? 'Switch to light mode'
                : 'Switch to dark mode'
        );
    }


    /* ---- 7. Toast Notification System ---- */
    window.showToast = function (message, type, duration) {
        type = type || 'info';
        duration = duration || 4000;

        var stack = document.querySelector('.toast-stack');
        if (!stack) {
            stack = document.createElement('div');
            stack.className = 'toast-stack';
            document.body.appendChild(stack);
        }

        var icons = {
            success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
            error:   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            info:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
        };

        var toast = document.createElement('div');
        toast.className = 'toast toast--' + type;
        toast.innerHTML =
            '<span class="toast__icon">' + (icons[type] || icons.info) + '</span>' +
            '<span class="toast__message">' + message + '</span>' +
            '<button class="toast__close" aria-label="Dismiss">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
            '</button>';

        stack.appendChild(toast);

        // Close button
        toast.querySelector('.toast__close').addEventListener('click', function () {
            dismissToast(toast);
        });

        // Auto dismiss
        var timer = setTimeout(function () { dismissToast(toast); }, duration);

        // Pause on hover
        toast.addEventListener('mouseenter', function () { clearTimeout(timer); });
        toast.addEventListener('mouseleave', function () {
            timer = setTimeout(function () { dismissToast(toast); }, 1500);
        });
    };

    function dismissToast(toast) {
        toast.style.animation = 'toastOut 0.25s ease forwards';
        setTimeout(function () { toast.remove(); }, 260);
    }

    // Convert Django messages to toasts
    function initDjangoMessageToasts() {
        document.querySelectorAll('.alert[data-toast]').forEach(function (el) {
            var message = el.textContent.trim();
            var type = 'info';
            if (el.classList.contains('alert--success')) type = 'success';
            else if (el.classList.contains('alert--error'))   type = 'error';
            else if (el.classList.contains('alert--warning')) type = 'warning';

            window.showToast(message, type);
            el.remove();
        });
    }


    /* ---- 8. Scroll Progress Bar ---- */
    function initScrollProgress() {
        var bar = document.getElementById('scrollProgressBar');
        if (!bar) return;

        function updateProgress() {
            var scrollTop = window.scrollY || document.documentElement.scrollTop;
            var docHeight = document.documentElement.scrollHeight - window.innerHeight;
            var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            bar.style.width = Math.min(pct, 100) + '%';
        }

        window.addEventListener('scroll', updateProgress, { passive: true });
        updateProgress();
    }


    /* ---- 9. Active Nav Link on Scroll (home page) ---- */
    function initActiveNavSync() {
        var sections = ['about', 'services', 'contact'];
        var links = {};

        sections.forEach(function (id) {
            var el = document.getElementById(id);
            var link = document.querySelector('.navbar__nav-link[href="#' + id + '"]');
            if (el && link) links[id] = { section: el, link: link };
        });

        if (!Object.keys(links).length) return;

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var id = entry.target.id;
                if (links[id]) {
                    links[id].link.classList.toggle('navbar__nav-link--active', entry.isIntersecting);
                }
            });
        }, { rootMargin: '-30% 0px -60% 0px' });

        Object.keys(links).forEach(function (id) {
            io.observe(links[id].section);
        });
    }


    /* ---- Apply saved theme before paint (avoid flash) ---- */
    (function applyThemeEarly() {
        var saved = localStorage.getItem('medicore-theme');
        if (saved === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    })();


    /* ---- Init ---- */
    document.addEventListener('DOMContentLoaded', function () {
        initReveal();
        initCountUp();
        initNavbarScroll();
        initSmoothScroll();
        initAutoDismiss();
        initThemeToggle();
        initDjangoMessageToasts();
        initScrollProgress();
        initActiveNavSync();
    });

})();




// center
const items = document.querySelectorAll(".item");

items.forEach(item => {

    const title = item.querySelector(".title");

    title.addEventListener("click", () => {

        items.forEach(i => {

            if(i !== item){

                i.classList.remove("active");

                i.querySelector(".toggle").innerHTML="+";

            }

        });

        item.classList.toggle("active");

        item.querySelector(".toggle").innerHTML =
            item.classList.contains("active") ? "−" : "+";

    });

});