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
    let maxX = 0;
    let maxY = 0;

    // ⚡ Bolt: DOM Object Pooling
    // Create a single target element once on load and reuse it
    // instead of repeatedly creating and removing DOM elements.
    const activeTarget = document.createElement('div');
    activeTarget.classList.add('target', 'hidden');
    gameArea.appendChild(activeTarget);
    activeTarget.addEventListener('mousedown', hitTarget);

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

        // ⚡ Bolt: Layout Caching
        // Cache game area dimensions to prevent layout thrashing
        // during the game loop.
        maxX = gameArea.clientWidth - 50; // 50 is approx target width
        maxY = gameArea.clientHeight - 50;

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
        activeTarget.classList.add('hidden');

        finalScoreDisplay.textContent = score;
        gameOverScreen.classList.remove('hidden');

        submitScore(score);
    }

    function spawnTarget() {
        if (!isPlaying) return;

        // Random position
        // Uses cached maxX and maxY values
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        activeTarget.style.left = `${randomX}px`;
        activeTarget.style.top = `${randomY}px`;
        activeTarget.classList.remove('hidden');
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
