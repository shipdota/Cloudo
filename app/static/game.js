document.addEventListener('DOMContentLoaded', () => {
    const gameArea = document.getElementById('game-area');
    const startScreen = document.getElementById('start-screen');
    const gameOverScreen = document.getElementById('game-over-screen');
    const scoreDisplay = document.getElementById('score');
    const timeDisplay = document.getElementById('time');
    const comboDisplay = document.getElementById('combo');
    const startBtn = document.getElementById('start-btn');
    const restartBtn = document.getElementById('restart-btn');
    const finalScoreDisplay = document.getElementById('final-score');

    let score = 0;
    let timeLeft = 30;
    let combo = 0;
    let gameInterval;
    let activeTarget = null;
    let targetTimeout = null;
    let isPlaying = false;

    const TARGET_TYPES = {
        NORMAL: { class: 'target-normal', points: 1, probability: 0.8 },
        BONUS: { class: 'target-bonus', points: 5, probability: 0.1 },
        PENALTY: { class: 'target-penalty', points: -5, probability: 0.1 }
    };

    // Audio effects (optional/placeholder)
    // const hitSound = new Audio('/static/hit.mp3');

    function startGame() {
        score = 0;
        timeLeft = 30;
        combo = 0;
        scoreDisplay.textContent = score;
        timeDisplay.textContent = timeLeft;
        if (comboDisplay) comboDisplay.textContent = combo;
        isPlaying = true;

        startScreen.classList.add('hidden');
        gameOverScreen.classList.add('hidden');

        spawnTarget();

        gameInterval = setInterval(() => {
            timeLeft--;
            timeDisplay.textContent = timeLeft;
            if (timeLeft <= 0) {
                endGame();
            }
        }, 1000);
    }

    function endGame() {
        clearInterval(gameInterval);
        if (targetTimeout) clearTimeout(targetTimeout);
        isPlaying = false;
        if (activeTarget) {
            activeTarget.remove();
            activeTarget = null;
        }

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying) return;

        if (activeTarget) activeTarget.remove();
        if (targetTimeout) clearTimeout(targetTimeout);

        const target = document.createElement('div');
        target.classList.add('target');

        // Determine target type
        const rand = Math.random();
        let currentType = TARGET_TYPES.NORMAL;
        let cumulativeProb = 0;

        for (const typeKey in TARGET_TYPES) {
            cumulativeProb += TARGET_TYPES[typeKey].probability;
            if (rand <= cumulativeProb) {
                currentType = TARGET_TYPES[typeKey];
                break;
            }
        }

        target.classList.add(currentType.class);
        target.dataset.points = currentType.points;

        // Random position
        const maxX = gameArea.clientWidth - 50;
        const maxY = gameArea.clientHeight - 50;

        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        target.style.left = `${randomX}px`;
        target.style.top = `${randomY}px`;

        target.addEventListener('mousedown', hitTarget);

        gameArea.appendChild(target);
        activeTarget = target;

        // Difficulty scaling: target duration decreases as score increases
        // Base duration 2s, minimum 0.5s. Reduces by 100ms for every 10 points.
        const duration = Math.max(500, 2000 - Math.floor(score / 10) * 100);

        // Target expiration logic
        targetTimeout = setTimeout(() => {
            if (activeTarget === target) {
                combo = 0; // Reset combo on miss/expire
                if (comboDisplay) comboDisplay.textContent = combo;
                spawnTarget(); // Respawn if expired
            }
        }, duration);
    }

    function hitTarget(e) {
        if (!isPlaying) return;

        const points = parseInt(e.target.dataset.points) || 1;

        if (points > 0) {
            combo++;
            // Apply combo multiplier to positive points
            const multiplier = Math.floor(combo / 5) + 1;
            score += points * multiplier;
        } else {
            // Penalty resets combo and applies fixed penalty
            combo = 0;
            score += points;
        }

        scoreDisplay.textContent = score;
        if (comboDisplay) comboDisplay.textContent = combo;

        spawnTarget();
    }

    async function submitScore(finalScore) {
        try {
            const response = await fetch('/api/submit-score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ score: finalScore })
            });

            if (response.ok) {
                console.log('Score submitted!');
                // Maybe show a "Saved!" toast
            } else {
                console.error('Failed to submit score');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    startBtn.addEventListener('click', startGame);
    restartBtn.addEventListener('click', startGame);
});
