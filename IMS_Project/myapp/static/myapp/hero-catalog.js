document.querySelectorAll('[data-hero-image]').forEach((image) => {
    const showFallback = () => {
        image.hidden = true;
        const fallback = image.nextElementSibling;
        if (fallback) {
            fallback.hidden = false;
        }
    };
    image.addEventListener('load', () => image.classList.add('is-loaded'), { once: true });
    image.addEventListener('error', showFallback, { once: true });
    if (image.complete) {
        if (image.naturalWidth > 0) {
            image.classList.add('is-loaded');
        } else {
            showFallback();
        }
    }
});
