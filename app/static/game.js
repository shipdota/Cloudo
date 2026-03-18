document.addEventListener('DOMContentLoaded', () => {
    const gameArea = document.getElementById('game-area');
    const startScreen = document.getElementById('start-screen');
    const gameOverScreen = document.getElementById('game-over-screen');
    const scoreDisplay = document.getElementById('score');
    const timeDisplay = document.getElementById('time');
    const startBtn = document.getElementById('start-btn');
    const restartBtn = document.getElementById('restart-btn');
    const finalScoreDisplay = document.getElementById('final-score');

    let score = 0;
    let timeLeft = 30;
    let gameInterval;
    let activeTarget = null;
    let isPlaying = false;

    // Cache game area dimensions to prevent layout thrashing on every spawn
    let cachedGameAreaWidth = gameArea.clientWidth;
    let cachedGameAreaHeight = gameArea.clientHeight;

    window.addEventListener('resize', () => {
        cachedGameAreaWidth = gameArea.clientWidth;
        cachedGameAreaHeight = gameArea.clientHeight;
    });

    // Audio effects (optional/placeholder)
    // const hitSound = new Audio('/static/hit.mp3');

    function startGame() {
        score = 0;
        timeLeft = 30;
        scoreDisplay.textContent = score;
        timeDisplay.textContent = timeLeft;
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

        const target = document.createElement('div');
        target.classList.add('target');

        // Random position
        // Use cached dimensions to avoid synchronous layout reflows (layout thrashing)
        const maxX = cachedGameAreaWidth - 50; // 50 is approx target width
        const maxY = cachedGameAreaHeight - 50;

        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        target.style.left = `${randomX}px`;
        target.style.top = `${randomY}px`;

        target.addEventListener('mousedown', hitTarget);

        gameArea.appendChild(target);
        activeTarget = target;
    }

    function hitTarget(e) {
        if (!isPlaying) return;

        // Visual feedback
        // maybe add a particle effect later

        score++;
        scoreDisplay.textContent = score;
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
