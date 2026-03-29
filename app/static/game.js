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
    let isPlaying = false;

    // Performance optimization: Layout caching
    let maxX = 0;
    let maxY = 0;

    // Performance optimization: DOM Object Pooling
    // Reuse a single target element instead of creating/destroying it constantly
    const activeTarget = document.createElement('div');
    activeTarget.classList.add('target');
    activeTarget.style.display = 'none';
    activeTarget.addEventListener('mousedown', hitTarget);
    gameArea.appendChild(activeTarget);

    // Update cached layout on resize to prevent bugs
    window.addEventListener('resize', () => {
        if (isPlaying) {
            maxX = gameArea.clientWidth - 50;
            maxY = gameArea.clientHeight - 50;
        }
    });

    // Audio effects (optional/placeholder)
    // const hitSound = new Audio('/static/hit.mp3');

    function startGame() {
        score = 0;
        timeLeft = 30;
        scoreDisplay.textContent = score;
        timeDisplay.textContent = timeLeft;
        isPlaying = true;

        // Cache dimensions to prevent layout thrashing
        maxX = gameArea.clientWidth - 50;
        maxY = gameArea.clientHeight - 50;

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

        // Hide instead of removing to preserve the DOM pool
        activeTarget.style.display = 'none';

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying) return;

        // Random position using cached layout dimensions
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        activeTarget.style.left = `${randomX}px`;
        activeTarget.style.top = `${randomY}px`;
        activeTarget.style.display = 'block';
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
