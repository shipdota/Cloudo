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

    // Object Pooling Optimization: Create target once to reduce DOM churn
    const pooledTarget = document.createElement('div');
    pooledTarget.classList.add('target', 'hidden');
    gameArea.appendChild(pooledTarget);

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

        // Ensure event listener is added only once
        if (!pooledTarget.hasAttribute('data-listener')) {
            pooledTarget.addEventListener('mousedown', hitTarget);
            pooledTarget.setAttribute('data-listener', 'true');
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
        pooledTarget.classList.add('hidden');
        activeTarget = null;

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying) return;

        // Random position
        // gameArea is relative
        const maxX = gameArea.clientWidth - 50; // 50 is approx target width
        const maxY = gameArea.clientHeight - 50;

        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        pooledTarget.style.left = `${randomX}px`;
        pooledTarget.style.top = `${randomY}px`;
        pooledTarget.classList.remove('hidden');

        activeTarget = pooledTarget;
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
