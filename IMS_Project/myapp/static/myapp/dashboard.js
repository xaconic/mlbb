(() => {
    const backdrop = document.getElementById('player-modal');
    const openButton = document.getElementById('open-player-modal');
    const closeButton = document.getElementById('close-player-modal');
    const cancelButton = document.getElementById('cancel-player-modal');
    const form = backdrop?.querySelector('form');
    const lookupButton = document.getElementById('lookup-player');
    const lookupError = document.getElementById('lookup-error');
    const preview = document.getElementById('player-preview');
    const previewGrid = document.getElementById('preview-grid');
    const updateButton = document.getElementById('update-player');
    const playerIdInput = form?.elements.namedItem('player_id');
    const serverInput = form?.elements.namedItem('server');
    const ignInput = form?.elements.namedItem('ign');
    let previousFocus = null;

    const starPairs = [
        {
            rank: document.getElementById('id_highest_rank'),
            stars: document.getElementById('id_highest_stars'),
            error: document.getElementById('highest-stars-validation'),
        },
        {
            rank: document.getElementById('id_current_rank'),
            stars: document.getElementById('id_current_stars'),
            error: document.getElementById('current-stars-validation'),
        },
    ].filter((pair) => pair.rank && pair.stars && pair.error);

    const mythicStarRanges = {
        Mythic: [1, 24],
        'Mythical Honor': [25, 49],
        'Mythical Glory': [50, 99],
        'Mythical Immortal': [100, null],
    };

    const validateStarPair = (pair) => {
        const range = mythicStarRanges[pair.rank.value];
        let message = '';

        if (range && pair.stars.value !== '') {
            const stars = Number(pair.stars.value);
            if (stars < range[0] || (range[1] !== null && stars > range[1])) {
                message = range[1] === null
                    ? `${pair.rank.value} requires at least ${range[0]} stars.`
                    : `${pair.rank.value} requires ${range[0]}-${range[1]} stars.`;
            }
        }

        pair.stars.setCustomValidity(message);
        pair.error.textContent = message;
        pair.error.hidden = !message;
        return !message;
    };

    starPairs.forEach((pair) => {
        pair.rank.addEventListener('change', () => validateStarPair(pair));
        pair.stars.addEventListener('input', () => validateStarPair(pair));
    });

    form?.addEventListener('submit', (event) => {
        starPairs.forEach(validateStarPair);
        if (!form.reportValidity()) {
            event.preventDefault();
        }
    });

    const focusFirstField = () => {
        const firstField = backdrop.querySelector('input:not([type="hidden"]), select');
        firstField?.focus();
    };

    const openModal = () => {
        if (!backdrop) {
            return;
        }
        previousFocus = document.activeElement;
        backdrop.hidden = false;
        document.body.classList.add('modal-open');
        focusFirstField();
    };

    const closeModal = () => {
        if (!backdrop) {
            return;
        }
        backdrop.hidden = true;
        document.body.classList.remove('modal-open');
        if (previousFocus instanceof HTMLElement) {
            previousFocus.focus();
        }
    };

    openButton?.addEventListener('click', openModal);
    document.querySelectorAll('[data-open-player-modal]').forEach((button) => {
        button.addEventListener('click', openModal);
    });
    document.getElementById('hero-add-player')?.addEventListener('click', openModal);
    closeButton?.addEventListener('click', closeModal);
    cancelButton?.addEventListener('click', closeModal);
    backdrop?.addEventListener('click', (event) => {
        if (event.target === backdrop) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && backdrop && !backdrop.hidden) {
            closeModal();
        }
    });

    const showLookupError = (message) => {
        lookupError.textContent = message;
        lookupError.hidden = false;
    };

    const showPlayerPreview = (player) => {
        const entries = [
            ['Player ID', player.player_id],
            ['Server ID', player.server],
            ['IGN', player.ign],
        ];
        previewGrid.replaceChildren();
        entries.forEach(([label, value]) => {
            const term = document.createElement('dt');
            const description = document.createElement('dd');
            term.textContent = label;
            description.textContent = value;
            previewGrid.append(term, description);
        });
        preview.hidden = false;
    };

    const fillExistingPlayer = (existing) => {
        for (const [name, value] of Object.entries(existing)) {
            const field = form.elements.namedItem(name);
            if (field && value !== null && value !== undefined) {
                field.value = value;
            }
        }
        starPairs.forEach(validateStarPair);
        updateButton.hidden = false;
    };

    const resetLookupState = () => {
        lookupError.hidden = true;
        preview.hidden = true;
        updateButton.hidden = true;
    };

    if (form && playerIdInput && serverInput && ignInput && lookupButton && lookupError && preview && previewGrid && updateButton) {
        [playerIdInput, serverInput].forEach((field) => {
            field.addEventListener('input', resetLookupState);
        });

        lookupButton.addEventListener('click', async () => {
            resetLookupState();

            const playerId = playerIdInput.value.trim();
            const serverId = serverInput.value.trim();
            if (!playerId || !serverId) {
                showLookupError('Enter both Player ID and Server ID before looking up a player.');
                (playerId ? serverInput : playerIdInput).focus();
                return;
            }

            const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]')?.value;
            const originalText = lookupButton.textContent;
            lookupButton.disabled = true;
            lookupButton.textContent = 'Looking up...';

            try {
                const response = await fetch(lookupButton.dataset.lookupUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        player_id: playerId,
                        server_id: serverId,
                    }),
                });
                const result = await response.json();

                if (!response.ok || !result.success || !result.player) {
                    showLookupError(result.error || 'The player lookup failed. Please try again.');
                    return;
                }

                const player = result.player;
                playerIdInput.value = player.player_id;
                serverInput.value = player.server;
                ignInput.value = player.ign;
                showPlayerPreview(player);

                if (player.duplicate && player.existing) {
                    fillExistingPlayer(player.existing);
                    showLookupError('This player is already in your roster. Review the existing details, then choose Update Existing Player to replace them.');
                }
            } catch (error) {
                console.error('Player lookup request failed.', error);
                showLookupError('The player lookup could not be completed. Check your connection and try again.');
            } finally {
                lookupButton.disabled = false;
                lookupButton.textContent = originalText;
            }
        });
    }

    const searchInput = document.getElementById('player-search');
    const roleFilter = document.getElementById('role-filter');
    const playerCards = Array.from(document.querySelectorAll('.player-card'));
    const noResults = document.getElementById('no-results');

    const filterPlayers = () => {
        const query = searchInput?.value.trim().toLocaleLowerCase() || '';
        const role = roleFilter?.value || '';
        let visibleCount = 0;

        playerCards.forEach((card) => {
            const matchesQuery = card.dataset.search.includes(query);
            const matchesRole = !role || card.dataset.role === role;
            const isVisible = matchesQuery && matchesRole;
            card.hidden = !isVisible;
            if (isVisible) {
                visibleCount += 1;
            }
        });

        if (noResults) {
            noResults.hidden = visibleCount !== 0 || playerCards.length === 0;
        }
    };

    searchInput?.addEventListener('input', filterPlayers);
    roleFilter?.addEventListener('change', filterPlayers);

    document.querySelectorAll('.toast').forEach((toast) => {
        window.setTimeout(() => toast.remove(), 4500);
    });

    if (backdrop && !backdrop.hidden) {
        document.body.classList.add('modal-open');
        focusFirstField();
    }
})();
