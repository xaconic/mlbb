(() => {
    const picker = document.querySelector('.hero-picker');
    if (!picker) return;

    const boxes = Array.from(picker.querySelectorAll('input[type="checkbox"]'));
    const portraits = Array.from(picker.querySelectorAll('.hero-art-tile img'));
    const count = document.getElementById('hero-count');
    const countValue = document.getElementById('hero-count-value');
    const submit = document.getElementById('profile-submit');
    const search = document.getElementById('hero-search');
    const roleFilter = document.getElementById('hero-role-filter');
    const catalog = JSON.parse(document.getElementById('hero-catalog')?.textContent || '[]');
    const heroesById = new Map(catalog.map((hero) => [String(hero.id), hero]));
    portraits.forEach((image) => {
        const useFallback = () => image.remove();
        image.addEventListener('error', useFallback, { once: true });
        if (image.complete && image.naturalWidth === 0) useFallback();
    });
    const update = () => {
        const selected = boxes.filter((box) => box.checked).length;
        if (countValue) countValue.textContent = String(selected);
        if (count) count.setAttribute('aria-label', `${selected} of 5 heroes selected`);
        if (submit) submit.disabled = selected !== 5;
        boxes.forEach((box) => {
            box.disabled = !box.checked && selected >= 5;
        });
    };

    boxes.forEach((box) => box.addEventListener('change', update));
    const filterHeroes = () => {
        const term = (search?.value || '').trim().toLowerCase();
        const role = roleFilter?.value || '';
        boxes.forEach((box) => {
            const hero = heroesById.get(box.value);
            const option = box.closest('.hero-option');
            if (!option || !hero) return;
            option.hidden = !hero.name.toLowerCase().includes(term) || Boolean(role && hero.role !== role);
        });
    };
    search?.addEventListener('input', filterHeroes);
    roleFilter?.addEventListener('change', filterHeroes);
    update();
})();
