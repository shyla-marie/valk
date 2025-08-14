import pygame
import random
import os
import json
import time

# Initialize Pygame and mixer for audio
print("Initializing Pygame...")
pygame.init()
if not pygame.get_init():
    print("Pygame initialization failed.")
pygame.mixer.init()
if not pygame.mixer.get_init():
    print("Mixer initialization failed.")

# Screen setup
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Ops Bimbos: Survival Dash")
print(f"Window created: {WIDTH}x{HEIGHT}")

# Colors (fallbacks)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load background
background = None
try:
    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    print("Background loaded successfully.")
except:
    print("Background image not found, using black background.")

# Load player sprite
player_img = None
try:
    player_img = pygame.image.load("player.png")
    player_img = pygame.transform.scale(player_img, (50, 50))  # Square (50x50)
    player_img.set_colorkey((0, 255, 0))  # Green screen transparency
    print("Player image loaded successfully.")
except:
    print("Player image not found, using white square.")
    player_img = pygame.Surface((50, 50))
    player_img.fill(WHITE)

# Player setup
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 250))  # Further down
player_speed = 3  # Kept moderate

# Bullet setup
bullets = []
bullet_speed = 5  # Reduced from 10
bullet_width = 5
bullet_height = 15

# Enemy setup
enemy_size = 40
enemy_base_speed = 0.5  # Reduced for slower movement
enemy_speed = enemy_base_speed
enemies = []  # Ensure empty at start
first_spawn_delay = 3000  # 3000 ms delay
last_spawn_time = 0
beat_interval = 606  # ~606 ms for 99 BPM

# Power-up setup
powerup_size = 30
powerups = []
powerup_effect_time = 5000
powerup_active = False
powerup_timer = 0

# Wave setup
wave = 1
wave_timer = pygame.time.get_ticks()
wave_duration = 10000
spawn_chance = 10  # Lowered for more frequent spawns
enemies_per_wave = 5  # Increased starting number, cap at 10
powerup_spawn_check = 20  # Lowered for more power-ups

# Score
score = 0
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Leaderboard
highscores = []  # Initialize globally
HIGHSCORE_FILE = "highscores.json"
try:
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            file_content = f.read().strip()
            highscores = json.loads(file_content) if file_content else []
            print("Highscores loaded successfully.")
except (json.JSONDecodeError, ValueError):
    print("Error loading highscores, starting with empty list.")
    highscores = []

# Music
try:
    pygame.mixer.music.load("theme_song.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    print("Music loaded and playing.")
except pygame.error as e:
    print(f"Error loading theme_song.wav: {e}")

def save_highscores():
    global highscores
    highscores.append(score)
    highscores.sort(reverse=True)
    highscores = highscores[:5]
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(highscores, f)
    print("Highscores saved.")

def spawn_enemy():
    x = random.randint(0, WIDTH - enemy_size)
    enemies.append([x, -2 * enemy_size, random.choice([-1, 1]) * random.uniform(0.5, 1.5)])  # Start higher
    print(f"Spawned enemy at {x}, {-2 * enemy_size}")

def spawn_powerup():
    x = random.randint(0, WIDTH - powerup_size)
    powerups.append([x, -2 * powerup_size])
    print(f"Spawned powerup at {x}, {-2 * powerup_size}")

# Main loop
running = True
game_over = False

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(player_rect.centerx - bullet_width // 2, player_rect.top, bullet_width, bullet_height)
                    bullets.append(bullet)
                    print(f"Shot bullet at {bullet}")
            else:
                if event.key == pygame.K_r:
                    # Reset game state
                    player_rect.center = (WIDTH // 2, HEIGHT - 250)
                    enemies.clear()
                    powerups.clear()
                    bullets.clear()
                    score = 0
                    wave = 1
                    spawn_chance = 10
                    enemy_speed = enemy_base_speed
                    powerup_active = False
                    game_over = False
                    last_spawn_time = 0
                    pygame.mixer.music.play(-1)
                    print("Game reset.")

    if not game_over:
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player_rect.y -= player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_rect.y += player_speed

        player_rect.clamp_ip(window.get_rect())

        # Wave progression
        if current_time - wave_timer > wave_duration:
            wave += 1
            spawn_chance = max(5, spawn_chance - 2)  # Moderate reduction
            enemy_speed += 0.1  # Slower increase
            enemies_per_wave = min(10, enemies_per_wave + 1)  # Cap at 10
            powerup_spawn_check = max(10, powerup_spawn_check - 2)  # More power-ups gradually
            wave_timer = current_time
            print(f"Wave {wave} started, speed: {enemy_speed}, enemies: {enemies_per_wave}")

        # Spawn with beat sync
        if current_time - last_spawn_time > first_spawn_delay or last_spawn_time == 0:
            if (current_time - last_spawn_time) % beat_interval < 10:  # Sync to ~606 ms beat
                for _ in range(enemies_per_wave):  # Spawn multiple enemies
                    if random.randint(1, spawn_chance) == 1:
                        spawn_enemy()
                if random.randint(1, powerup_spawn_check) == 1:  # Moderate power-up frequency
                    spawn_powerup()
                last_spawn_time = current_time
            print(f"Spawn check at {current_time}, enemies queued: {len(enemies)}")  # Debug spawn

        # Update enemies
        for enemy in enemies[:]:
            enemy[0] += enemy[2]  # Horizontal movement
            enemy[1] += enemy_speed if not powerup_active else enemy_speed / 2
            if enemy[1] > HEIGHT:
                enemies.remove(enemy)
                score += 1
                print(f"Enemy missed, score: {score}")
            if enemy[0] < 0 or enemy[0] > WIDTH - enemy_size:
                enemy[2] = -enemy[2]  # Bounce horizontal
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
            if player_rect.colliderect(enemy_rect) and enemy[1] > 0:  # Avoid top collisions
                print(f"Collision detected at {current_time}ms, enemy at {enemy}, player at {player_rect}")
                game_over = True
                save_highscores()
                pygame.mixer.music.stop()

        # Update bullets
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
                if bullet.colliderect(enemy_rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 10
                    print(f"Enemy killed, score: {score}")
                    break

        # Update power-ups
        for powerup in powerups[:]:
            powerup[1] += enemy_speed / 2
            if powerup[1] > HEIGHT:
                powerups.remove(powerup)
            powerup_rect = pygame.Rect(powerup[0], powerup[1], powerup_size, powerup_size)
            if player_rect.colliderect(powerup_rect):
                powerups.remove(powerup)
                powerup_active = True
                powerup_timer = current_time
                print("Power-up collected, slowing enemies.")

        if powerup_active and current_time - powerup_timer > powerup_effect_time:
            powerup_active = False
            print("Power-up effect ended.")

        # Draw
        if background:
            window.blit(background, (0, 0))
        else:
            window.fill(BLACK)
        window.blit(player_img, player_rect)
        for enemy in enemies:
            pygame.draw.rect(window, RED, (enemy[0], enemy[1], enemy_size, enemy_size))
        for powerup in powerups:
            pygame.draw.rect(window, GREEN, (powerup[0], powerup[1], powerup_size, powerup_size))
        for bullet in bullets:
            pygame.draw.rect(window, YELLOW, bullet)

        score_text = font.render(f"Score: {score} | Wave: {wave}", True, WHITE)
        window.blit(score_text, (10, 10))
        if powerup_active:
            window.blit(small_font.render("Slow Enemies Active!", True, GREEN), (10, 50))
        pygame.display.flip()  # Ensure flip is here
        print("Frame drawn at", current_time)  # Confirm drawing

    else:
        # Game over screen
        if background:
            window.blit(background, (0, 0))
        else:
            window.fill(BLACK)
        game_over_text = font.render(f"Game Over! Final Score: {score}", True, RED)
        window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        restart_text = small_font.render("Press 'R' to Restart", True, WHITE)
        window.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
        leaderboard_text = font.render("Leaderboard:", True, WHITE)
        window.blit(leaderboard_text, (WIDTH // 2 - leaderboard_text.get_width() // 2, HEIGHT // 2 + 100))
        for i, hs in enumerate(highscores):
            hs_text = small_font.render(f"{i+1}. {hs}", True, WHITE)
            window.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 + 130 + i * 30))

        pygame.display.flip()
        clock.tick(FPS)

pygame.mixer.music.stop()
pygame.quit()