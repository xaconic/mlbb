/**
 * DAWNROSTER — Immersive MLBB-Themed Background System
 *
 * Creates a multi-layered animated background with:
 * - Floating MLBB hero portraits with parallax
 * - Ambient particle system
 * - Atmospheric lighting
 * - Cursor-reactive effects on desktop
 * - Performance-conscious rendering
 */
(() => {
    'use strict';

    /* ── Respect user preferences ── */
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ── Featured MLBB Heroes (from database catalog) ── */
    const FEATURED_HEROES = [
        { name: 'Ling', role: 'Jungle', url: 'https://static.wikia.nocookie.net/mobile-legends/images/c/ca/Hero841-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153020' },
        { name: 'Lancelot', role: 'Jungle', url: 'https://static.wikia.nocookie.net/mobile-legends/images/2/29/Hero471-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145518' },
        { name: 'Kagura', role: 'Mid Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/e/ef/Hero251-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145310' },
        { name: 'Gusion', role: 'Jungle', url: 'https://static.wikia.nocookie.net/mobile-legends/images/9/94/Hero561-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145610' },
        { name: 'Hayabusa', role: 'Jungle', url: 'https://static.wikia.nocookie.net/mobile-legends/images/c/cb/Hero211-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145247' },
        { name: 'Granger', role: 'Gold Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/7/7c/Hero791-icon.png/revision/latest/scale-to-width-down/200?cb=20241108062800' },
        { name: 'Benedetta', role: 'Exp Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/4/47/Hero971-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153134' },
        { name: 'Wanwan', role: 'Gold Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/2/24/Hero891-icon.png/revision/latest/scale-to-width-down/200?cb=20250118142135' },
        { name: 'Chou', role: 'Exp Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/a/a9/Hero261-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145315' },
        { name: 'Lesley', role: 'Gold Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/8/82/Hero531-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145551' },
        { name: 'Fanny', role: 'Jungle', url: 'https://static.wikia.nocookie.net/mobile-legends/images/7/78/Hero171-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145223' },
        { name: 'Tigreal', role: 'Roam', url: 'https://static.wikia.nocookie.net/mobile-legends/images/f/f2/Hero061-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145106' },
        { name: 'Miya', role: 'Gold Lane', url: 'https://static.wikia.nocookie.net/mobile-legends/images/8/8c/Hero011-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145035' },
    ];

    /* ── Shuffle helper ── */
    function shuffle(arr) {
        const a = [...arr];
        for (let i = a.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [a[i], a[j]] = [a[j], a[i]];
        }
        return a;
    }

    /* ── Build the background DOM ── */
    function buildBackground() {
        const bg = document.createElement('div');
        bg.className = 'auth-bg';
        bg.setAttribute('aria-hidden', 'true');

        bg.innerHTML = `
            <div class="auth-bg__base"></div>
            <div class="auth-bg__fog"></div>
            <div class="auth-bg__lines">
                <div class="auth-bg__line auth-bg__line--1"></div>
                <div class="auth-bg__line auth-bg__line--2"></div>
                <div class="auth-bg__line auth-bg__line--3"></div>
            </div>
            <div class="auth-bg__vline auth-bg__vline--1"></div>
            <div class="auth-bg__vline auth-bg__vline--2"></div>
            <div class="auth-bg__vline auth-bg__vline--3"></div>
            <div class="auth-bg__particles"></div>
            <div class="auth-bg__overlay"></div>
        `;

        /* Add hero portrait orbs in background */
        const heroes = shuffle(FEATURED_HEROES).slice(0, 8);
        heroes.forEach((hero, i) => {
            const orb = document.createElement('div');
            orb.className = `auth-bg__hero auth-bg__hero--${i + 1}`;
            const img = document.createElement('img');
            img.src = hero.url;
            img.alt = '';
            img.loading = 'lazy';
            img.decoding = 'async';
            img.referrerPolicy = 'strict-origin-when-cross-origin';
            img.addEventListener('load', () => orb.classList.add('is-loaded'));
            img.addEventListener('error', () => {
                orb.style.background = 'radial-gradient(circle, rgba(86,217,245,0.06), transparent)';
                orb.classList.add('is-loaded');
            });
            orb.appendChild(img);
            bg.insertBefore(orb, bg.querySelector('.auth-bg__overlay'));
        });

        document.body.prepend(bg);
        return bg;
    }

    /* ── Particle System (Canvas) ── */
    function initParticles(container) {
        if (prefersReducedMotion) return;

        const canvas = document.createElement('canvas');
        canvas.style.cssText = 'width:100%;height:100%;pointer-events:none;';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        let particles = [];
        let animId;
        let isHidden = document.hidden;

        function resize() {
            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            canvas.width = container.clientWidth * dpr;
            canvas.height = container.clientHeight * dpr;
            ctx.scale(dpr, dpr);
        }

        function createParticles() {
            const count = Math.min(Math.floor(window.innerWidth / 25), 50);
            particles = [];
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * container.clientWidth,
                    y: Math.random() * container.clientHeight,
                    size: Math.random() * 2 + 0.5,
                    speedX: (Math.random() - 0.5) * 0.3,
                    speedY: (Math.random() - 0.5) * 0.2 - 0.1,
                    opacity: Math.random() * 0.4 + 0.1,
                    hue: Math.random() > 0.5 ? 190 : 225,
                });
            }
        }

        function draw() {
            if (isHidden) {
                animId = requestAnimationFrame(draw);
                return;
            }

            const w = container.clientWidth;
            const h = container.clientHeight;
            ctx.clearRect(0, 0, w, h);

            for (const p of particles) {
                p.x += p.speedX;
                p.y += p.speedY;

                /* Wrap around */
                if (p.x < -10) p.x = w + 10;
                if (p.x > w + 10) p.x = -10;
                if (p.y < -10) p.y = h + 10;
                if (p.y > h + 10) p.y = -10;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, 80%, 75%, ${p.opacity})`;
                ctx.fill();

                /* Subtle glow */
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, 80%, 75%, ${p.opacity * 0.15})`;
                ctx.fill();
            }

            animId = requestAnimationFrame(draw);
        }

        resize();
        createParticles();
        draw();

        window.addEventListener('resize', () => {
            resize();
            createParticles();
        });

        document.addEventListener('visibilitychange', () => {
            isHidden = document.hidden;
        });
    }

    /* ── Parallax on Desktop ── */
    function initParallax(bg) {
        if (prefersReducedMotion || 'ontouchstart' in window) return;

        const heroes = bg.querySelectorAll('.auth-bg__hero');
        const fog = bg.querySelector('.auth-bg__fog');
        let ticking = false;

        document.addEventListener('mousemove', (e) => {
            if (ticking) return;
            ticking = true;

            requestAnimationFrame(() => {
                const mx = (e.clientX / window.innerWidth - 0.5) * 2;
                const my = (e.clientY / window.innerHeight - 0.5) * 2;

                heroes.forEach((hero, i) => {
                    const depth = 1 + (i % 3) * 0.5;
                    const x = mx * 12 * depth;
                    const y = my * 8 * depth;
                    hero.style.transform = `translate(${x}px, ${y}px)`;
                });

                if (fog) {
                    fog.style.transform = `translate(${mx * 5}px, ${my * 3}px)`;
                }

                ticking = false;
            });
        });
    }

    /* ── Hero Showcase (Story Panel Cards) ── */
    function initHeroShowcase() {
        const showcase = document.querySelector('.auth-hero-showcase');
        if (!showcase) return;

        const positions = ['far-left', 'left', 'center', 'right', 'far-right'];
        const heroes = shuffle(FEATURED_HEROES).slice(0, 5);

        heroes.forEach((hero, i) => {
            const card = document.createElement('div');
            card.className = `auth-hero-card auth-hero-card--${positions[i]}`;
            const img = document.createElement('img');
            img.src = hero.url;
            img.alt = `${hero.name} - ${hero.role}`;
            img.loading = i === 2 ? 'eager' : 'lazy';
            img.decoding = 'async';
            img.referrerPolicy = 'strict-origin-when-cross-origin';
            img.addEventListener('error', () => {
                card.style.background = 'linear-gradient(135deg, #111E32, #162640)';
                card.innerHTML = `<span style="color:#56D9F5;font-weight:700;font-size:1.5rem;display:grid;place-items:center;height:100%">${hero.name[0]}</span>`;
            });
            card.appendChild(img);
            showcase.appendChild(card);
        });

        /* Rotate showcase heroes every 6 seconds */
        if (!prefersReducedMotion) {
            let currentSet = heroes;
            setInterval(() => {
                const newHeroes = shuffle(FEATURED_HEROES).slice(0, 5);
                const cards = showcase.querySelectorAll('.auth-hero-card img');
                cards.forEach((img, i) => {
                    if (newHeroes[i] && img.src !== newHeroes[i].url) {
                        img.style.opacity = '0';
                        setTimeout(() => {
                            img.src = newHeroes[i].url;
                            img.alt = `${newHeroes[i].name} - ${newHeroes[i].role}`;
                            img.style.opacity = '1';
                        }, 400);
                    }
                });
                currentSet = newHeroes;
            }, 8000);
        }
    }

    /* ── Submit Button Loading State ── */
    function initFormBehavior() {
        const form = document.querySelector('.auth-form');
        if (!form) return;

        form.addEventListener('submit', () => {
            const btn = form.querySelector('.auth-submit');
            if (btn && !btn.disabled) {
                btn.classList.add('is-loading');
                btn.disabled = true;
                /* Re-enable after 8s in case of network issues */
                setTimeout(() => {
                    btn.classList.remove('is-loading');
                    btn.disabled = false;
                }, 8000);
            }
        });
    }

    /* ── Password Toggle (enhanced from existing) ── */
    /* ── Initialize ── */
    function init() {
        const bg = buildBackground();
        initParticles(bg.querySelector('.auth-bg__particles'));
        initParallax(bg);
        initHeroShowcase();
        initFormBehavior();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

