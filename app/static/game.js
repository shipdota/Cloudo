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

    // Cache layout dimensions to prevent layout thrashing (forced synchronous layout) during gameplay
    let cachedMaxX = 0;
    let cachedMaxY = 0;

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

        // Cache game area dimensions once per game start
        cachedMaxX = gameArea.clientWidth - 50; // 50 is approx target width
        cachedMaxY = gameArea.clientHeight - 50;

        // Create a single target element and pool it instead of recreating and destroying it on every click
        if (!activeTarget) {
            activeTarget = document.createElement('div');
            activeTarget.classList.add('target');
            activeTarget.addEventListener('mousedown', hitTarget);
            gameArea.appendChild(activeTarget);
        } else {
            activeTarget.style.display = 'block';
        }

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

        // Hide instead of removing to maintain the DOM element pool
        if (activeTarget) {
            activeTarget.style.display = 'none';
        }

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying || !activeTarget) return;

        // Random position using cached dimensions to avoid layout thrashing
        const randomX = Math.floor(Math.random() * cachedMaxX);
        const randomY = Math.floor(Math.random() * cachedMaxY);

        // Simply update position of the existing element
        activeTarget.style.left = `${randomX}px`;
        activeTarget.style.top = `${randomY}px`;
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
