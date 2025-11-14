const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 500;
canvas.height = 500;

let player = { x: 240, y: 450, size: 20, speed: 5 };
let obstacles = [];
let orbs = [];
let gameRunning = false;
let score = 0;

document.addEventListener("keydown", (e) => {
    if (!gameRunning) return;

    if (e.key === "ArrowLeft" && player.x > 0) {
        player.x -= player.speed;
    } else if (e.key === "ArrowRight" && player.x < canvas.width - player.size) {
        player.x += player.speed;
    }
});

function spawnObstacle() {
    let size = Math.random() * 30 + 20;
    obstacles.push({
        x: Math.random() * (canvas.width - size),
        y: -size,
        size: size,
        speed: Math.random() * 3 + 2
    });
}

function spawnOrb() {
    orbs.push({
        x: Math.random() * 480,
        y: -20,
        size: 15,
        speed: 2
    });
}

function isColliding(a, b) {
    return (
        a.x < b.x + b.size &&
        a.x + a.size > b.x &&
        a.y < b.y + b.size &&
        a.y + a.size > b.y
    );
}

function update() {
    if (!gameRunning) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#29dfff";
    ctx.fillRect(player.x, player.y, player.size, player.size);

    ctx.fillStyle = "red";
    obstacles.forEach((obs, index) => {
        obs.y += obs.speed;
        ctx.fillRect(obs.x, obs.y, obs.size, obs.size);

        if (isColliding(player, obs)) {
            alert("Game Over! Final Score: " + score);
            resetGame();
        }

        if (obs.y > 500) obstacles.splice(index, 1);
    });

    ctx.fillStyle = "yellow";
    orbs.forEach((orb, index) => {
        orb.y += orb.speed;
        ctx.beginPath();
        ctx.arc(orb.x, orb.y, orb.size, 0, Math.PI * 2);
        ctx.fill();

        if (isColliding(player, orb)) {
            score += 10;
            orbs.splice(index, 1);
        }

        if (orb.y > 500) orbs.splice(index, 1);
    });

    requestAnimationFrame(update);
}

document.getElementById("startBtn").addEventListener("click", () => {
    if (!gameRunning) {
        gameRunning = true;
        score = 0;
        spawnInterval = setInterval(spawnObstacle, 800);
        orbInterval = setInterval(spawnOrb, 2000);
        update();
    }
});

function resetGame() {
    gameRunning = false;
    obstacles = [];
    orbs = [];
    clearInterval(spawnInterval);
    clearInterval(orbInterval);
}