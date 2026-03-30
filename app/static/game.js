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

    // ⚡ Bolt: Caching layout dimensions and pooling the target element to avoid layout thrashing and memory churn
    let maxX = 0;
    let maxY = 0;

    const pooledTarget = document.createElement('div');
    pooledTarget.classList.add('target');
    pooledTarget.style.display = 'none';

    // Add event listener directly to pooledTarget
    pooledTarget.addEventListener('mousedown', hitTarget);
    gameArea.appendChild(pooledTarget);

    function updateGameAreaBounds() {
        maxX = gameArea.clientWidth - 50; // 50 is approx target width
        maxY = gameArea.clientHeight - 50;
    }

    window.addEventListener('resize', updateGameAreaBounds);
    updateGameAreaBounds(); // Initial bounds calculation

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

        // Ensure bounds are updated before spawning
        updateGameAreaBounds();
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
        pooledTarget.style.display = 'none';

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying) return;

        // ⚡ Bolt: Update inline styles of pooled element instead of creating new DOM nodes
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        pooledTarget.style.left = `${randomX}px`;
        pooledTarget.style.top = `${randomY}px`;
        pooledTarget.style.display = 'block';
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
