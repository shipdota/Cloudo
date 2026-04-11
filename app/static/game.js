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

    // Performance optimization: DOM Object Pooling
    // Instead of creating and destroying DOM elements rapidly, we create one and reuse it
    let pooledTarget = document.createElement('div');
    pooledTarget.classList.add('target', 'hidden');
    pooledTarget.addEventListener('mousedown', hitTarget);
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

        // Hide the pooled target instead of removing it
        pooledTarget.classList.add('hidden');

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

        // Reposition and unhide the pooled target
        pooledTarget.style.left = `${randomX}px`;
        pooledTarget.style.top = `${randomY}px`;
        pooledTarget.classList.remove('hidden');
    }

    function hitTarget(e) {
        if (!isPlaying) return;

        // Visual feedback
        // maybe add a particle effect later

        // Instantly hide the target to prevent double-clicks
        pooledTarget.classList.add('hidden');

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
