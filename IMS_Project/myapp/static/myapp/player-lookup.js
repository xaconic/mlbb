(() => {
    const button = document.getElementById('lookup-player');
    const message = document.getElementById('lookup-message');
    const form = button?.closest('form');
    if (!button || !message || !form) return;

    const value = (name) => form.querySelector(`[name="${name}"]`)?.value.trim() || '';
    const setIfOptionExists = (name, candidate) => {
        if (candidate === null || candidate === undefined) return;
        const field = form.querySelector(`[name="${name}"]`);
        if (field && Array.from(field.options).some((option) => option.value === String(candidate))) {
            field.value = String(candidate);
        }
    };

    button.addEventListener('click', async () => {
        const playerId = value('player_id');
        const serverId = value('server');
        if (!playerId || !serverId) {
            message.textContent = 'Enter both your Player ID and Server ID first.';
            message.dataset.state = 'error';
            return;
        }

        const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]')?.value || '';
        const originalLabel = button.textContent;
        button.disabled = true;
        button.textContent = 'Looking up…';
        message.textContent = '';
        message.dataset.state = '';
        try {
            const response = await fetch('/api/player-lookup/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({player_id: playerId, server_id: serverId}),
            });
            let result;
            try {
                result = await response.json();
            } catch {
                throw new Error('The lookup service returned malformed data.');
            }
            if (!response.ok || !result.success || !result.player) {
                throw new Error(result.error || 'The lookup service returned an unexpected response.');
            }

            const player = result.player;
            form.querySelector('[name="ign"]').value = player.ign;
            setIfOptionExists('main_role', player.main_role);
            setIfOptionExists('current_rank', player.current_rank);
            setIfOptionExists('highest_rank', player.highest_rank);
            if (player.current_stars !== null && player.current_stars !== undefined) {
                form.querySelector('[name="current_stars"]').value = player.current_stars;
            }
            if (player.highest_stars !== null && player.highest_stars !== undefined) {
                form.querySelector('[name="highest_stars"]').value = player.highest_stars;
            }
            if (player.win_rate !== null && player.win_rate !== undefined) {
                form.querySelector('[name="win_rate"]').value = player.win_rate;
            }
            message.textContent = result.player.duplicate
                ? 'Game name loaded. These IDs already appear in the system; check ownership before saving.'
                : 'Game name loaded. Review your profile details before saving.';
            message.dataset.state = result.player.duplicate ? 'warning' : 'success';
        } catch (error) {
            message.textContent = error instanceof Error
                ? error.message
                : 'The MLBB lookup service could not be reached. Please try again.';
            message.dataset.state = 'error';
        } finally {
            button.disabled = false;
            button.textContent = originalLabel;
        }
    });
})();
