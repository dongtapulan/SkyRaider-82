import pygame
from settings import WIDTH, HEIGHT, FPS
from utils import load_image, load_sound
from player import Player
from enemy import Enemy
from bullet import Bullet, EnemyBullet
import random
import os
import math
from boss import Boss, Boss2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Raider BattleWorld")
clock = pygame.time.Clock()
   
# Asset Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
SND_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Load Assets
player_img = load_image(os.path.join(IMG_DIR, 'player.png'))
enemy_img = load_image(os.path.join(IMG_DIR, 'enemy.png'))
enemy2_img = load_image(os.path.join(IMG_DIR, 'enemy2.png'))
enemy3_img = load_image(os.path.join(IMG_DIR, 'enemy3.png'))
bullet_img = load_image(os.path.join(IMG_DIR, 'bullet.png'))
cloud_img = load_image(os.path.join(IMG_DIR, 'cloud.png'))
explosion_img = load_image(os.path.join(IMG_DIR, 'explosion.png'))
boss_img = load_image(os.path.join(IMG_DIR, 'boss.png'))
boss2_img = load_image(os.path.join(IMG_DIR, 'boss2.png'))
boss_bullet_img = load_image(os.path.join(IMG_DIR, 'boss_bullet.png'))
spreadshot_powerup_img = load_image(os.path.join(IMG_DIR, 'spreadshot_powerup.png'))
shield_powerup_img = load_image(os.path.join(IMG_DIR, 'shield_powerup.png'))
health_powerup_img = load_image(os.path.join(IMG_DIR, 'health_powerup.png'))

shoot_sound = load_sound(os.path.join(SND_DIR, 'shoot.wav'))
explosion_sound = load_sound(os.path.join(SND_DIR, 'explosion.wav'))
pygame.mixer.music.load(os.path.join(SND_DIR, 'background_music.mp3'))
pygame.mixer.music.play(-1)
engine_sound = load_sound(os.path.join(SND_DIR, 'engine.wav'))  # Use your actual filename
engine_sound.set_volume(1.0)  # Adjust volume as needed
engine_sound.play(-1)         # -1 means loop forever

# --- PowerUp Class (place near other sprite classes, not in the main loop) ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, image, x, y):
        super().__init__()
        self.kind = kind  # 'spread', 'shield', 'health'
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# --- Cloud and Wind Classes ---
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = cloud_img.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -40)
        self.speed = random.uniform(1.0, 3.0)
        self.parallax = random.uniform(0.3, 0.7)
        self.alpha = 0  # Start fully transparent for fade-in
        self.max_alpha = random.randint(120, 200)
        self.fading_in = True

    def update(self):
        # Move vertically with parallax
        self.rect.y += self.speed * self.parallax

        # Fade in
        if self.fading_in:
            self.alpha += 2
            if self.alpha >= self.max_alpha:
                self.alpha = self.max_alpha
                self.fading_in = False
        # Fade out as cloud nears bottom of screen
        elif self.rect.y > HEIGHT * 0.7:
            self.alpha -= 1.5
            if self.alpha < 0:
                self.alpha = 0

        self.image.set_alpha(int(self.alpha))

        # Remove cloud if fully faded out or off screen
        if self.rect.top > HEIGHT or self.alpha == 0:
            self.kill()

class WindParticle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.length = random.randint(10, 30)
        self.speed = random.uniform(2, 5)
        self.parallax = random.uniform(0.6, 1.0)
        self.alpha = random.randint(80, 160)
        self.color = (200, 220, 255, self.alpha)

    def update(self):
        self.x += self.speed * self.parallax
        if self.x > WIDTH:
            self.x = -self.length
            self.y = random.randint(0, HEIGHT)
            self.length = random.randint(10, 30)
            self.speed = random.uniform(2, 5)
            self.parallax = random.uniform(0.6, 1.0)
            self.alpha = random.randint(80, 160)
            self.color = (200, 220, 255, self.alpha)

    def draw(self, surface):
        s = pygame.Surface((self.length, 2), pygame.SRCALPHA)
        pygame.draw.line(s, self.color, (0, 1), (self.length, 1), 2)
        surface.blit(s, (self.x, self.y))

# Groups
player = Player(player_img)
player.spreadshot_timer = 0
player.shield_timer = 0
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
cloud_group = pygame.sprite.Group()
wind_particles = [WindParticle() for _ in range(10)]  # Reduced from 25
explosion_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
boss_bullet_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()

# Assign enemy_bullet_group to Enemy class for shooting
Enemy.enemy_bullet_group = enemy_bullet_group

# Game State
running = True
enemy_spawn_timer = 0
shoot_cooldown = 0
cloud_spawn_timer = 0
score = 0
player_health = 5
player_max_health = 5
player_hit_timer = 0
boss_spawned = False
boss_spawn_timer = random.randint(1200, 2400)  # Frames until boss spawns (20-40 seconds at 60 FPS)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, image=explosion_img, duration=6):
        super().__init__()
        # Optionally scale down the explosion image if it's too big
        scale = 0.6  # 60% of original size, adjust as needed
        size = (int(image.get_width() * scale), int(image.get_height() * scale))
        self.base_image = pygame.transform.smoothscale(image, size).convert_alpha()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=center)
        self.duration = duration
        self.current_frame = 0

    def update(self):
        self.current_frame += 1
        # Fade out quickly
        alpha = max(0, 255 - int(255 * (self.current_frame / self.duration)))
        self.image = self.base_image.copy()
        self.image.set_alpha(alpha)
        if self.current_frame >= self.duration:
            self.kill()

# --- Font Configuration ---
FONT_PATH = os.path.join(ASSETS_DIR, 'font', 'ARCADE_R.TTF')  # Change to your font filename
font = pygame.font.Font(FONT_PATH, 24)
small_font = pygame.font.Font(FONT_PATH, 12)

def main_menu():
    # Create temporary groups for menu animation
    menu_clouds = pygame.sprite.Group()
    menu_wind_particles = [WindParticle() for _ in range(10)]
    menu_cloud_spawn_timer = 0

    menu_running = True
    while menu_running:
        clock.tick(FPS)
        # --- Animated Sky ---
        screen.fill((100, 180, 255))  # blue sky

        # Sun Glow/Gradient
        sun_center = (WIDTH // 2, 80)
        for r in range(120, 0, -20):
            alpha = max(0, 60 - r // 2)
            sun_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(sun_surface, (255, 255, 200, alpha), (r, r), r)
            screen.blit(sun_surface, (sun_center[0] - r, sun_center[1] - r))

        # Sea Mist (Breeze)
        wave_base = HEIGHT - 80
        mist_surface = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        for i in range(5):
            alpha = 30 - i*5
            pygame.draw.ellipse(
                mist_surface,
                (220, 240, 255, alpha),
                (random.randint(-40, 40), 10 + i*8, WIDTH + 80, 30 + i*6)
            )
        screen.blit(mist_surface, (0, wave_base - 30))

        # Clouds (animated)
        menu_cloud_spawn_timer += 1
        if menu_cloud_spawn_timer > 50 and len(menu_clouds) < 8:
            menu_clouds.add(Cloud())
            menu_cloud_spawn_timer = 0
        menu_clouds.update()
        menu_clouds.draw(screen)

        # Wind Particles (animated)
        for wind in menu_wind_particles:
            wind.update()
            wind.draw(screen)

        # --- Menu Text ---
        title = font.render("SkyRaider '82", True, (255, 255, 255))
        prompt = small_font.render("Press SPACE to Start", True, (0, 0, 0))
        quit_text = small_font.render("Press Q to Quit", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # (game_over_screen function moved above main loop; this duplicate can be removed)
                
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu_running = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

main_menu()

def upgrade_screen():
    points = 5
    strength = 0
    durability = 0
    damage = 0
    selected = 0  # 0: Strength, 1: Durability, 2: Damage
    upgrade_font = pygame.font.Font(FONT_PATH, 12)
    running = True

    while running:
        clock.tick(FPS)
        screen.fill((30, 60, 120))
        title = upgrade_font.render("UPGRADE YOUR PLANE", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        options = [
            f"Strength: {strength}  (More Health)",
            f"Durability: {durability}  (Strength Bonus)",
            f"Damage: {damage}  (More Damage, Bosses Weaker)"
        ]
        for i, text in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opt = upgrade_font.render(text, True, color)
            screen.blit(opt, (WIDTH // 2 - opt.get_width() // 2, 140 + i * 40))

        pts_text = upgrade_font.render(f"Points Left: {points}", True, (255, 255, 255))
        screen.blit(pts_text, (WIDTH // 2 - pts_text.get_width() // 2, 270))

        instr = upgrade_font.render("Arrow keys to select, SPACE to add, ENTER to confirm", True, (180, 220, 255))
        screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, 320))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                if event.key == pygame.K_SPACE and points > 0:
                    if selected == 0:
                        strength += 1
                    elif selected == 1:
                        durability += 1
                    elif selected == 2:
                        damage += 1
                    points -= 1
                if event.key == pygame.K_RETURN and points == 0:
                    running = False
    return strength, durability, damage

# --- Before story_screen() call ---
strength, durability, damage = upgrade_screen()

def story_screen():
    story_lines = [
        "HERE WE ARE, IN THE BATTLEWORLD",
        "",
        "YOU ARE THE LAST ACE PILOT OF THE SKY RAIDERS.",
        "",
        "ENEMY SQUADRONS HAVE INVADED THE SKIES.",
        "",
        "DEFEND YOUR HOMELAND AND SURVIVE THE ONSLAUGHT!",
        "",
        "PRESS SPACE TO BEGIN YOUR MISSION..."
    ]
    showing = True
    line_shown = 0
    last_update = pygame.time.get_ticks()
    line_delay = 700  # ms between lines

    while showing:
        clock.tick(FPS)
        screen.fill((60, 120, 200))
        # Draw animated story text
        for i in range(line_shown):
            text = small_font.render(story_lines[i], True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 120 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if line_shown < len(story_lines):
                    # Show all lines instantly if SPACE is pressed early
                    line_shown = len(story_lines)
                else:
                    showing = False

        # Reveal next line after delay
        now = pygame.time.get_ticks()
        if line_shown < len(story_lines) and now - last_update > line_delay:
            line_shown += 1
            last_update = now

story_screen()

# Apply upgrades
player_max_health = 5 + (strength * 5) + int(strength * 5 * 0.2 * durability)
player_health = player_max_health
player.health = player_max_health  # If your Player class uses this
player.strength = strength
player.durability = durability
player.damage = 1 + damage  # Use this in your bullet/boss hit logic

boss_health_multiplier = 1 - 0.05 * damage  # Bosses have less health per damage point

# When spawning a boss, apply the health multiplier:
# boss = Boss(boss_img, bullet_img)
# boss.health = int(boss.health * boss_health_multiplier)
# boss.max_health = boss.health

def game_over_screen(final_score):
    showing = True
    while showing:
        clock.tick(FPS)
        screen.fill((40, 40, 40))
        over_text = font.render("You Died", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {final_score}", True, (255, 255, 255))
        prompt_text = small_font.render("Press SPACE to return to Main Menu", True, (200, 200, 200))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                showing = False

def reset_game_state():
    global score, player_health, player_max_health, player_hit_timer
    global enemy_spawn_timer, shoot_cooldown, cloud_spawn_timer
    global boss_spawned, boss_spawn_timer
    player.rect.centerx = WIDTH // 2
    player.rect.bottom = HEIGHT - 60
    score = 0
    player_health = 5
    player_max_health = 5
    player_hit_timer = 0
    enemy_spawn_timer = 0
    shoot_cooldown = 0
    cloud_spawn_timer = 0
    bullet_group.empty()
    enemy_group.empty()
    enemy_bullet_group.empty()
    explosion_group.empty()
    cloud_group.empty()
    boss_group.empty()
    boss_bullet_group.empty()
    boss_spawned = False
    boss_spawn_timer = random.randint(1200, 2400)  # Reset for new game

running = True
paused = False
while running:
    clock.tick(FPS)
    # --- Draw Sky ---
    screen.fill((100, 180, 255))  # blue sky

    # --- Draw Sun Glow/Gradient ---
    sun_center = (WIDTH // 2, 80)
    for r in range(120, 0, -20):
        alpha = max(0, 60 - r // 2)
        sun_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(sun_surface, (255, 255, 200, alpha), (r, r), r)
        screen.blit(sun_surface, (sun_center[0] - r, sun_center[1] - r))

    # Define wave_base for sea mist vertical position
    wave_base = HEIGHT - 80

    # --- Draw Sea Mist (Breeze) ---
    mist_surface = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
    for i in range(5):
        alpha = 30 - i*5
        pygame.draw.ellipse(
            mist_surface,
            (220, 240, 255, alpha),
            (random.randint(-40, 40), 10 + i*8, WIDTH + 80, 30 + i*6)
        )
    screen.blit(mist_surface, (0, wave_base - 30))

    # --- Draw Clouds ---
    cloud_spawn_timer += 1
    if cloud_spawn_timer > 50 and len(cloud_group) < 8:
        cloud_group.add(Cloud())
        cloud_spawn_timer = 0
    cloud_group.update()
    cloud_group.draw(screen)

    # --- Wind Particles ---
    for wind in wind_particles:
        wind.update()
        wind.draw(screen)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused

    if not paused:
        # --- Player input ---
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Optional: Make engine louder when moving
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN] or \
           keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
            engine_sound.set_volume(1.0)
        else:
            engine_sound.set_volume(0.5)

        # --- Improved shooting with cooldown ---
        if shoot_cooldown > 0:
            shoot_cooldown -= 1
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            if len(bullet_group) < 10:
                offset = 15
                left_pos = (player.rect.centerx - offset, player.rect.top)
                right_pos = (player.rect.centerx + offset, player.rect.top)
                if player.spreadshot_timer > 0:
                    # Spreadshot: 3 bullets
                    center_pos = (player.rect.centerx, player.rect.top)
                    bullet_left = Bullet(bullet_img, left_pos)
                    bullet_center = Bullet(bullet_img, center_pos)
                    bullet_right = Bullet(bullet_img, right_pos)
                    # Give left/right bullets a slight angle
                    bullet_left.angle = -15
                    bullet_right.angle = 15
                    bullet_group.add(bullet_left, bullet_center, bullet_right)
                else:
                    bullet_left = Bullet(bullet_img, left_pos)
                    bullet_right = Bullet(bullet_img, right_pos)
                    bullet_group.add(bullet_left, bullet_right)
                shoot_sound.play()
                shoot_cooldown = 10

        # --- Spawn enemies frequently ---
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 50:
            x = random.randint(0, WIDTH - 50)
            r = random.random()
            if r < 0.25:
                from enemy import Enemy3
                enemy = Enemy3(enemy3_img, x, -50)
            elif r < 0.65:
                from enemy import Enemy2
                enemy = Enemy2(enemy2_img, x, -50)
            else:
                enemy = Enemy(enemy_img, x, -50)
            enemy_group.add(enemy)
            enemy.enemy_bullet_group = enemy_bullet_group
            enemy_spawn_timer = 0

        # --- Spawn boss frequently ---
        if not boss_spawned and random.random() < 0.008:
            if random.random() < 0.5:
                boss = Boss(boss_img, boss_bullet_img)
            else:
                boss = Boss2(boss2_img, boss_bullet_img)
            boss_group.add(boss)
            boss_spawned = True

        # Update and draw boss
        for boss in boss_group:
            new_bullets = boss.update()
            if new_bullets:
                for b in new_bullets:
                    boss_bullet_group.add(b)
            boss.draw_health_bar(screen)
        boss_group.draw(screen)

        # Update and draw boss bullets
        for bullet in boss_bullet_group:
            bullet.update()
        boss_bullet_group.draw(screen)

        # --- Update ---
        bullet_group.update()
        enemy_group.update()
        enemy_bullet_group.update()
        explosion_group.update()
        powerup_group.update()

        # --- Remove off-screen enemies ---
        for enemy in enemy_group.copy():
            if enemy.rect.top > HEIGHT:
                enemy.kill()

        # --- Player bullets hit enemies and spawn power-ups ---
        for bullet in bullet_group.copy():
            hits = pygame.sprite.spritecollide(bullet, enemy_group, True)
            if hits:
                bullet.kill()
                explosion_sound.play()
                score += 100
                for enemy in hits:
                    explosion = Explosion(enemy.rect.center)
                    explosion_group.add(explosion)
                    # --- Power-up spawn (increased to 25% chance) ---
                    if random.random() < 0.25:
                        kind = random.choice(['spread', 'shield', 'health'])
                        if kind == 'spread':
                            img = spreadshot_powerup_img
                        elif kind == 'shield':
                            img = shield_powerup_img
                        else:
                            img = health_powerup_img
                        powerup = PowerUp(kind, img, enemy.rect.centerx, enemy.rect.centery)
                        powerup_group.add(powerup)

        # --- Power-up collection ---
        hits = pygame.sprite.spritecollide(player, powerup_group, True)
        for powerup in hits:
            if powerup.kind == 'spread':
                player.spreadshot_timer = 600  # 10 seconds at 60 FPS
            elif powerup.kind == 'shield':
                player.shield_timer = 600
            elif powerup.kind == 'health':
                if player_health < player_max_health:
                    player_health += 1

        # --- Power-up timers ---
        if player.spreadshot_timer > 0:
            player.spreadshot_timer -= 1
        if player.shield_timer > 0:
            player.shield_timer -= 1

        # --- Draw Sprites ---
        player_group.draw(screen)
        bullet_group.draw(screen)
        enemy_group.draw(screen)
        enemy_bullet_group.draw(screen)
        explosion_group.draw(screen)
        powerup_group.draw(screen)

        # --- Draw Shield Effect ---
        if player.shield_timer > 0:
            shield_radius = player.rect.width
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (100, 255, 100, 80), (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (player.rect.centerx - shield_radius, player.rect.centery - shield_radius))

        # --- Draw Health Bar above player ---
        bar_width = 60
        bar_height = 8
        bar_x = player.rect.centerx - bar_width // 2
        bar_y = player.rect.top - 16
        health_ratio = player_health / player_max_health
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

        # --- Draw Score ---
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        # --- Enemy bullets hit player ---
        if player_hit_timer > 0:
            player_hit_timer -= 1
        else:
            if player.shield_timer > 0:
                pass  # Invincible while shield is active
            else:
                hits = pygame.sprite.spritecollide(player, enemy_bullet_group, True)
                if hits:
                    player_health -= 1
                    player_hit_timer = 30
                    explosion_sound.play()
                    explosion = Explosion(player.rect.center)
                    explosion_group.add(explosion)
                    if player_health <= 0:
                        game_over_screen(score)
                        reset_game_state()
                        main_menu()

            # Player collides with enemies
            hits = pygame.sprite.spritecollide(player, enemy_group, True)
            if hits:
                player_health -= 1
                player_hit_timer = 30
                explosion_sound.play()
                explosion = Explosion(player.rect.center)
                explosion_group.add(explosion)
                if player_health <= 0:
                    game_over_screen(score)
                    reset_game_state()
                    main_menu()

            # --- Boss bullets hit player ---
            hits = pygame.sprite.spritecollide(player, boss_bullet_group, True)
            if hits:
                player_health -= 1
                player_hit_timer = 30
                explosion_sound.play()
                explosion = Explosion(player.rect.center)
                explosion_group.add(explosion)
                if player_health <= 0:
                    game_over_screen(score)
                    reset_game_state()
                    main_menu()

    else:
        # Draw "Paused" overlay
        pause_text = font.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 40))
        info_text = small_font.render("Press P to Resume", True, (255, 255, 255))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.flip()
        continue  # Skip the rest of the loop

    # --- Check bullet collisions with boss ---
    for bullet in bullet_group.copy():
        hits = pygame.sprite.spritecollide(bullet, boss_group, False)
        if hits:
            bullet.kill()
            for boss in hits:
                boss.health -= 5
                explosion = Explosion(bullet.rect.center)
                explosion_group.add(explosion)
                if boss.health <= 0:
                    # Boss explosion
                    explosion_sound.play()
                    explosion = Explosion(boss.rect.center)
                    explosion_group.add(explosion)
                    boss.kill()
                    score += 1000
                    boss_spawned = False  # Allow another boss to spawn

    for _ in range(2):
        island_x = random.randint(0, WIDTH - 120)
        island_y = random.randint(HEIGHT // 6, HEIGHT // 2)
        island_w = random.randint(80, 140)
        island_h = random.randint(20, 40)
        island_color = (random.randint(60, 90), random.randint(120, 180), random.randint(40, 80))
        pygame.draw.ellipse(screen, island_color, (island_x, island_y, island_w, island_h))

for y in range(HEIGHT):
    color = (
        100,
        180 - int(80 * y / HEIGHT),
        255 - int(100 * y / HEIGHT)
    )
    pygame.draw.line(screen, color, (0, y), (WIDTH, y))

water_base = HEIGHT - 80
for i in range(8):
    wave_y = water_base + i * 10 + int(5 * math.sin(pygame.time.get_ticks() / 400 + i))
    pygame.draw.ellipse(screen, (80, 180, 255, 60), (0, wave_y, WIDTH, 20))