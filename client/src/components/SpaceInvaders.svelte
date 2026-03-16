<script lang="ts">
  // Game constants
  const CANVAS_WIDTH = 640;
  const CANVAS_HEIGHT = 480;
  const PLAYER_WIDTH = 40;
  const PLAYER_HEIGHT = 20;
  const PLAYER_SPEED = 5;
  const BULLET_WIDTH = 3;
  const BULLET_HEIGHT = 10;
  const BULLET_SPEED = 7;
  const INVADER_WIDTH = 30;
  const INVADER_HEIGHT = 20;
  const INVADER_ROWS = 4;
  const INVADER_COLS = 8;
  const INVADER_PADDING = 12;
  const INVADER_DROP = 20;
  const INVADER_BASE_SPEED = 1;
  const SHOOT_COOLDOWN = 250;

  interface Bullet {
    x: number;
    y: number;
    active: boolean;
  }

  interface Invader {
    x: number;
    y: number;
    alive: boolean;
    row: number;
  }

  // Game state
  let canvas: HTMLCanvasElement | undefined = $state();
  let gameState: 'idle' | 'playing' | 'gameover' = $state('idle');
  let score = $state(0);
  let lives = $state(3);
  let highScore = $state(0);

  // Player
  let playerX = $state(CANVAS_WIDTH / 2 - PLAYER_WIDTH / 2);

  // Bullets
  let bullets: Bullet[] = $state([]);
  let lastShotTime = $state(0);

  // Invaders
  let invaders: Invader[] = $state([]);
  let invaderDirection = $state(1);
  let invaderSpeed = $state(INVADER_BASE_SPEED);
  let invaderMoveTimer = $state(0);
  let invaderMoveInterval = $state(30);

  // Enemy bullets
  let enemyBullets: Bullet[] = $state([]);
  let enemyShootTimer = $state(0);

  // Input
  let keysPressed = $state(new Set<string>());

  // Derived
  let aliveCount = $derived(invaders.filter((inv) => inv.alive).length);
  let isPlaying = $derived(gameState === 'playing');
  let statusText = $derived(
    gameState === 'idle'
      ? 'Press Start to Play'
      : gameState === 'gameover'
        ? `Game Over! Final Score: ${score}`
        : ''
  );

  function initInvaders(): void {
    const newInvaders: Invader[] = [];
    const totalWidth = INVADER_COLS * (INVADER_WIDTH + INVADER_PADDING) - INVADER_PADDING;
    const startX = (CANVAS_WIDTH - totalWidth) / 2;
    for (let row = 0; row < INVADER_ROWS; row++) {
      for (let col = 0; col < INVADER_COLS; col++) {
        newInvaders.push({
          x: startX + col * (INVADER_WIDTH + INVADER_PADDING),
          y: 40 + row * (INVADER_HEIGHT + INVADER_PADDING),
          alive: true,
          row,
        });
      }
    }
    invaders = newInvaders;
  }

  function startGame(): void {
    score = 0;
    lives = 3;
    playerX = CANVAS_WIDTH / 2 - PLAYER_WIDTH / 2;
    bullets = [];
    enemyBullets = [];
    invaderDirection = 1;
    invaderSpeed = INVADER_BASE_SPEED;
    invaderMoveTimer = 0;
    invaderMoveInterval = 30;
    enemyShootTimer = 0;
    initInvaders();
    gameState = 'playing';
  }

  function shoot(): void {
    const now = Date.now();
    if (now - lastShotTime < SHOOT_COOLDOWN) return;
    lastShotTime = now;
    bullets.push({
      x: playerX + PLAYER_WIDTH / 2 - BULLET_WIDTH / 2,
      y: CANVAS_HEIGHT - PLAYER_HEIGHT - 20 - BULLET_HEIGHT,
      active: true,
    });
  }

  function enemyShoot(): void {
    const aliveInvaders = invaders.filter((inv) => inv.alive);
    if (aliveInvaders.length === 0) return;
    const shooter = aliveInvaders[Math.floor(Math.random() * aliveInvaders.length)];
    enemyBullets.push({
      x: shooter.x + INVADER_WIDTH / 2 - BULLET_WIDTH / 2,
      y: shooter.y + INVADER_HEIGHT,
      active: true,
    });
  }

  function update(): void {
    if (gameState !== 'playing') return;

    // Player movement
    if (keysPressed.has('ArrowLeft') || keysPressed.has('a')) {
      playerX = Math.max(0, playerX - PLAYER_SPEED);
    }
    if (keysPressed.has('ArrowRight') || keysPressed.has('d')) {
      playerX = Math.min(CANVAS_WIDTH - PLAYER_WIDTH, playerX + PLAYER_SPEED);
    }

    // Move bullets
    for (const bullet of bullets) {
      bullet.y -= BULLET_SPEED;
      if (bullet.y < 0) bullet.active = false;
    }
    bullets = bullets.filter((b) => b.active);

    // Move enemy bullets
    for (const bullet of enemyBullets) {
      bullet.y += BULLET_SPEED * 0.6;
      if (bullet.y > CANVAS_HEIGHT) bullet.active = false;
    }
    enemyBullets = enemyBullets.filter((b) => b.active);

    // Enemy shooting
    enemyShootTimer++;
    if (enemyShootTimer > 60) {
      enemyShoot();
      enemyShootTimer = 0;
    }

    // Move invaders
    invaderMoveTimer++;
    if (invaderMoveTimer >= invaderMoveInterval) {
      invaderMoveTimer = 0;
      let shouldDrop = false;

      for (const inv of invaders) {
        if (!inv.alive) continue;
        if (
          (invaderDirection > 0 && inv.x + INVADER_WIDTH + invaderSpeed >= CANVAS_WIDTH) ||
          (invaderDirection < 0 && inv.x - invaderSpeed <= 0)
        ) {
          shouldDrop = true;
          break;
        }
      }

      if (shouldDrop) {
        invaderDirection *= -1;
        for (const inv of invaders) {
          inv.y += INVADER_DROP;
        }
        // Speed up slightly
        invaderMoveInterval = Math.max(5, invaderMoveInterval - 1);
      } else {
        for (const inv of invaders) {
          inv.x += invaderSpeed * invaderDirection;
        }
      }
    }

    // Bullet-invader collision
    for (const bullet of bullets) {
      if (!bullet.active) continue;
      for (const inv of invaders) {
        if (!inv.alive) continue;
        if (
          bullet.x < inv.x + INVADER_WIDTH &&
          bullet.x + BULLET_WIDTH > inv.x &&
          bullet.y < inv.y + INVADER_HEIGHT &&
          bullet.y + BULLET_HEIGHT > inv.y
        ) {
          bullet.active = false;
          inv.alive = false;
          const pointsByRow = [40, 30, 20, 10];
          score += pointsByRow[inv.row] ?? 10;
          // Speed up as invaders are destroyed
          invaderMoveInterval = Math.max(5, Math.floor(30 * (aliveCount / (INVADER_ROWS * INVADER_COLS))));
        }
      }
    }

    // Enemy bullet-player collision
    const playerY = CANVAS_HEIGHT - PLAYER_HEIGHT - 20;
    for (const bullet of enemyBullets) {
      if (!bullet.active) continue;
      if (
        bullet.x < playerX + PLAYER_WIDTH &&
        bullet.x + BULLET_WIDTH > playerX &&
        bullet.y < playerY + PLAYER_HEIGHT &&
        bullet.y + BULLET_HEIGHT > playerY
      ) {
        bullet.active = false;
        lives--;
        if (lives <= 0) {
          gameState = 'gameover';
          if (score > highScore) highScore = score;
        }
      }
    }

    // Check if invaders reached player
    for (const inv of invaders) {
      if (inv.alive && inv.y + INVADER_HEIGHT >= playerY) {
        gameState = 'gameover';
        if (score > highScore) highScore = score;
        break;
      }
    }

    // All invaders destroyed — next wave
    if (aliveCount === 0) {
      invaderSpeed += 0.5;
      initInvaders();
      enemyBullets = [];
    }
  }

  function draw(): void {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Stars background
    ctx.fillStyle = 'rgba(148, 163, 184, 0.3)';
    for (let i = 0; i < 50; i++) {
      const sx = (i * 137.5) % CANVAS_WIDTH;
      const sy = (i * 97.3) % CANVAS_HEIGHT;
      ctx.fillRect(sx, sy, 1, 1);
    }

    if (gameState === 'idle') {
      ctx.fillStyle = '#e2e8f0';
      ctx.font = 'bold 28px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('SPACE INVADERS', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 40);
      ctx.font = '16px Inter, sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.fillText('Arrow keys or A/D to move · Space to shoot', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 10);
      ctx.fillText('Press Start to begin', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 40);
      return;
    }

    // Draw player ship
    const playerY = CANVAS_HEIGHT - PLAYER_HEIGHT - 20;
    ctx.fillStyle = '#3b82f6';
    ctx.beginPath();
    ctx.moveTo(playerX + PLAYER_WIDTH / 2, playerY);
    ctx.lineTo(playerX + PLAYER_WIDTH, playerY + PLAYER_HEIGHT);
    ctx.lineTo(playerX, playerY + PLAYER_HEIGHT);
    ctx.closePath();
    ctx.fill();
    // Ship glow
    ctx.shadowColor = '#3b82f6';
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw invaders
    const invaderColors = ['#f43f5e', '#f97316', '#a3e635', '#22d3ee'];
    for (const inv of invaders) {
      if (!inv.alive) continue;
      ctx.fillStyle = invaderColors[inv.row] ?? '#22d3ee';

      // Simple invader shape
      const ix = inv.x;
      const iy = inv.y;
      const iw = INVADER_WIDTH;
      const ih = INVADER_HEIGHT;

      ctx.fillRect(ix + 4, iy, iw - 8, ih * 0.4);
      ctx.fillRect(ix, iy + ih * 0.3, iw, ih * 0.4);
      ctx.fillRect(ix + 2, iy + ih * 0.6, 6, ih * 0.4);
      ctx.fillRect(ix + iw - 8, iy + ih * 0.6, 6, ih * 0.4);
      // Eyes
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(ix + 8, iy + ih * 0.35, 4, 4);
      ctx.fillRect(ix + iw - 12, iy + ih * 0.35, 4, 4);
      ctx.fillStyle = invaderColors[inv.row] ?? '#22d3ee';
    }

    // Draw player bullets
    ctx.fillStyle = '#60a5fa';
    ctx.shadowColor = '#60a5fa';
    ctx.shadowBlur = 6;
    for (const bullet of bullets) {
      ctx.fillRect(bullet.x, bullet.y, BULLET_WIDTH, BULLET_HEIGHT);
    }
    ctx.shadowBlur = 0;

    // Draw enemy bullets
    ctx.fillStyle = '#f43f5e';
    ctx.shadowColor = '#f43f5e';
    ctx.shadowBlur = 6;
    for (const bullet of enemyBullets) {
      ctx.fillRect(bullet.x, bullet.y, BULLET_WIDTH, BULLET_HEIGHT);
    }
    ctx.shadowBlur = 0;

    // Game over overlay
    if (gameState === 'gameover') {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
      ctx.fillStyle = '#f43f5e';
      ctx.font = 'bold 36px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('GAME OVER', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 20);
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '20px Inter, sans-serif';
      ctx.fillText(`Score: ${score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 20);
      ctx.font = '14px Inter, sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.fillText('Press Restart to play again', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 55);
    }
  }

  // Game loop effect
  $effect(() => {
    if (!canvas) return;

    let animationId: number;

    function gameLoop(): void {
      update();
      draw();
      animationId = requestAnimationFrame(gameLoop);
    }

    animationId = requestAnimationFrame(gameLoop);

    return () => {
      cancelAnimationFrame(animationId);
    };
  });

  // Keyboard input effect
  $effect(() => {
    function handleKeyDown(e: KeyboardEvent): void {
      if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' ', 'a', 'd'].includes(e.key)) {
        e.preventDefault();
      }
      keysPressed = new Set([...keysPressed, e.key]);
      if (e.key === ' ' && gameState === 'playing') {
        shoot();
      }
    }

    function handleKeyUp(e: KeyboardEvent): void {
      const next = new Set(keysPressed);
      next.delete(e.key);
      keysPressed = next;
    }

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  });
</script>

<div class="flex flex-col items-center gap-6" data-testid="space-invaders-game">
  <!-- Score bar -->
  <div class="flex items-center justify-between w-full max-w-[640px] px-2">
    <div class="flex items-center gap-6">
      <div class="text-slate-300 text-sm font-medium">
        Score: <span class="text-blue-400 font-bold text-lg" data-testid="score-display">{score}</span>
      </div>
      <div class="text-slate-300 text-sm font-medium">
        Lives:
        <span class="text-blue-400 font-bold" data-testid="lives-display">
          {#each Array(lives) as _}
            <span aria-label="life" role="img">💙</span>
          {/each}
          {#if lives <= 0}
            <span class="text-slate-500">0</span>
          {/if}
        </span>
      </div>
    </div>
    <div class="text-slate-400 text-sm">
      High Score: <span class="text-yellow-400 font-bold" data-testid="high-score-display">{highScore}</span>
    </div>
  </div>

  <!-- Canvas -->
  <div class="rounded-xl overflow-hidden border border-slate-700 shadow-xl shadow-blue-500/5">
    <canvas
      bind:this={canvas}
      width={CANVAS_WIDTH}
      height={CANVAS_HEIGHT}
      class="block bg-slate-950"
      aria-label="Space Invaders game canvas"
      role="img"
      data-testid="game-canvas"
    ></canvas>
  </div>

  <!-- Controls -->
  <div class="flex items-center gap-4">
    {#if gameState === 'idle' || gameState === 'gameover'}
      <button
        onclick={startGame}
        class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-lg hover:shadow-blue-600/20 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        data-testid="start-button"
      >
        {gameState === 'gameover' ? 'Restart' : 'Start Game'}
      </button>
    {/if}
  </div>

  <!-- Instructions -->
  {#if gameState === 'idle'}
    <div class="text-center text-slate-400 text-sm max-w-md" data-testid="game-instructions">
      <p class="mb-1"><kbd class="px-2 py-0.5 bg-slate-700 rounded text-slate-300 text-xs">←</kbd> <kbd class="px-2 py-0.5 bg-slate-700 rounded text-slate-300 text-xs">→</kbd> or <kbd class="px-2 py-0.5 bg-slate-700 rounded text-slate-300 text-xs">A</kbd> <kbd class="px-2 py-0.5 bg-slate-700 rounded text-slate-300 text-xs">D</kbd> to move</p>
      <p><kbd class="px-2 py-0.5 bg-slate-700 rounded text-slate-300 text-xs">Space</kbd> to shoot</p>
    </div>
  {/if}

  <!-- Status text for screen readers -->
  {#if statusText}
    <p class="sr-only" aria-live="polite" data-testid="game-status">{statusText}</p>
  {/if}
</div>
