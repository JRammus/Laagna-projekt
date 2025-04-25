import pygame
import random
import os

# Init
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

# Screen
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("K0SMOSE VALLUTAJAD VOL 38")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game Variables
player_speed = 8
player_lives = 7
player_score = 0
game_over = False
game_ended = False
boost_active = False
boss_flash_timer = 0
nitro_active = False
konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
               pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
               pygame.K_b, pygame.K_a]
konami_input = []
konami_code_triggered = False
boss_defeated = False

# Cooldowns
player_last_shot = 0
player_shoot_delay = 300
nitro_duration = 5000
boost_duration = 5000

# Shake & Zoom
shake_intensity = 10
shake_duration = 200
shake_timer = 0
shake_offset = pygame.Vector2(0, 0)
zoom_timer = 0
zoom_duration = 0

# Assets
img_path = os.getcwd()
player_image = pygame.transform.scale(pygame.image.load("player_ship1.png"), (84, 84))
player_nitro_image = pygame.transform.scale(pygame.image.load("player_nitro.png"), (94, 94))
bullet_image = pygame.transform.scale(pygame.image.load("bullet1.png"), (30, 60))
enemy_image = pygame.transform.scale(pygame.image.load("enemy_ship1.png"), (64, 64))
upgrade_image = pygame.transform.scale(pygame.image.load("upgrade.png"), (72, 72))
nitro_upgrade_image = pygame.transform.scale(pygame.image.load("nitro_upgrade.png"), (72, 72))
boss_image = pygame.transform.scale(pygame.image.load("boss_ship1.png"), (192, 192))
start_screen_img = pygame.transform.scale(pygame.image.load("start_screen.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
death_screen_img = pygame.transform.scale(pygame.image.load("death_screen.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# Sounds
laser_sound = pygame.mixer.Sound("laser.mp3")
laser_sound.set_volume(0.5)
nitro_sound = pygame.mixer.Sound("nitro.mp3")
nitro_sound.set_volume(1.0)
oneup_sound = pygame.mixer.Sound("1up.mp3")
oneup_sound.set_volume(1.0)
boss_music = pygame.mixer.Sound("boss_music.mp3")
boss_music.set_volume(0.8)
theme_song = pygame.mixer.Sound("theme_song.mp3")
theme_song.set_volume(0.3)
theme_song.play(-1)

# Fonts
font = pygame.font.Font(None, 50)
game_over_font = pygame.font.Font(None, 100)

# Functions
def trigger_shake(intensity=10, duration=200):
    global shake_timer, shake_intensity, shake_duration
    shake_timer = pygame.time.get_ticks()
    shake_intensity = intensity
    shake_duration = duration

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.health = 100

    def update(self, keys):
        if keys[pygame.K_LEFT]: self.rect.x -= player_speed
        if keys[pygame.K_RIGHT]: self.rect.x += player_speed
        if keys[pygame.K_UP]: self.rect.y -= player_speed
        if keys[pygame.K_DOWN]: self.rect.y += player_speed
        self.rect.clamp_ip(screen.get_rect())

    def activate_nitro(self):
        global nitro_active, nitro_time
        self.image = player_nitro_image
        nitro_active = True
        nitro_time = pygame.time.get_ticks()
        nitro_sound.play()

    def deactivate_nitro(self):
        global nitro_active
        self.image = player_image
        nitro_active = False

    def reset_health(self):
        self.health = 500

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def update(self):
        self.rect.y += self.direction * 10
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50),
                                                random.randint(50, SCREEN_HEIGHT // 3)))
        self.speed_x = random.choice([-4.5, 4.5])
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
        if pygame.time.get_ticks() - self.last_shot > random.randint(500, 1500):
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.bottom, 1))
            laser_sound.play()
            self.last_shot = pygame.time.get_ticks()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.speed_x = 6
        self.speed_y = 3
        self.health = 20
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if self.rect.centerx < player.rect.centerx:
            self.rect.x += self.speed_x
        elif self.rect.centerx > player.rect.centerx:
            self.rect.x -= self.speed_x

        self.rect.y = min(self.rect.y + self.speed_y, SCREEN_HEIGHT // 2)
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        now = pygame.time.get_ticks()
        if now - self.last_shot > 1000:
            enemy_bullets.add(Bullet(self.rect.centerx - 30, self.rect.bottom, 1))
            enemy_bullets.add(Bullet(self.rect.centerx + 30, self.rect.bottom, 1))
            laser_sound.play()
            self.last_shot = now

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

class Upgrade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = upgrade_image
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -50))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class NitroUpgrade(Upgrade):
    def __init__(self):
        super().__init__()
        self.image = nitro_upgrade_image

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        self.speed = random.uniform(0.5, 2.5)
        self.radius = random.choice([1, 2]) * 2

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.__init__()

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

class ShootingStar:
    def __init__(self):
        self.x = random.randint(-100, SCREEN_WIDTH // 2)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.speed_x = random.uniform(8, 12)
        self.speed_y = random.uniform(4, 6)
        self.length = random.randint(60, 100)
        self.life = 60

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            end_pos = (int(self.x + self.length), int(self.y + self.length // 2))
            pygame.draw.line(surface, (255, 255, 200), (int(self.x), int(self.y)), end_pos, 2)

# Groups
player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bosses = pygame.sprite.Group()
upgrades = pygame.sprite.Group()
nitro_upgrades = pygame.sprite.Group()
stars = [Star() for _ in range(150)]
shooting_stars = []

# Timers
clock = pygame.time.Clock()
enemy_spawn_time = pygame.time.get_ticks()
upgrade_spawn_time = pygame.time.get_ticks()
shooting_star_timer = pygame.time.get_ticks()
enemy_spawn_delay = 1250
upgrade_spawn_delay = 3000

# START SCREEN
show_start_screen = True
while show_start_screen:
    screen.blit(start_screen_img, (0, 0))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            show_start_screen = False
show_death_screen = False

# GAME LOOP
while not game_over:
    screen.fill(BLACK)
    now = pygame.time.get_ticks()

    # Shake
    if now - shake_timer < shake_duration:
        shake_offset.x = random.randint(-shake_intensity, shake_intensity)
        shake_offset.y = random.randint(-shake_intensity, shake_intensity)
    else:
        shake_offset.xy = (0, 0)

    # Background
    for star in stars: star.update(); star.draw(screen)
    if now - shooting_star_timer > random.randint(7000, 12000):
        shooting_stars.append(ShootingStar())
        shooting_star_timer = now
    for s in shooting_stars[:]:
        s.update(); s.draw(screen)
        if s.life <= 0: shooting_stars.remove(s)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            game_over = True
        if event.type == pygame.KEYDOWN:
            konami_input.append(event.key)
            if len(konami_input) > len(konami_code): konami_input.pop(0)
            if konami_input == konami_code and not konami_code_triggered:
                player.reset_health(); player.activate_nitro()
                boost_active = True; konami_code_triggered = True
                player_lives = 1000
            if event.key == pygame.K_SPACE and now - player_last_shot > player_shoot_delay:
                player_last_shot = now; laser_sound.play()
                if konami_code_triggered or boost_active:
                    bullets.add(Bullet(player.rect.centerx - 15, player.rect.top))
                    bullets.add(Bullet(player.rect.centerx + 15, player.rect.top))
                else:
                    bullets.add(Bullet(player.rect.centerx, player.rect.top))

    # Spawns
    if player_score >= 30 and not boss_defeated and len(bosses) == 0:
        bosses.add(Boss()); theme_song.stop(); boss_music.play(-1)
    if now - enemy_spawn_time > enemy_spawn_delay:
        enemies.add(Enemy()); enemy_spawn_time = now
    if now - upgrade_spawn_time > upgrade_spawn_delay:
        upgrades.add(random.choice([Upgrade(), NitroUpgrade()]))
        upgrade_spawn_time = now

    # Collisions
    if pygame.sprite.spritecollide(player, enemy_bullets, True) and not nitro_active:
        player_lives -= 1; trigger_shake()
        if player_lives <= 0:
            game_over = True
            death_screen_time = pygame.time.get_ticks()
            show_death_screen = True

    hits = pygame.sprite.spritecollide(player, upgrades, True)
    for hit in hits:
        if isinstance(hit, NitroUpgrade): player.activate_nitro()
        else: player_lives += 1; oneup_sound.play()

    enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    player_score += len(enemy_hits)

    for boss in bosses:
        if pygame.sprite.spritecollide(boss, bullets, True):
            trigger_shake()
            if boss.take_damage():
                boss.kill(); boss_defeated = True; player_score += 10
                boss_flash_timer = 10
                boss_music.stop(); theme_song.play(-1)
                trigger_shake(30, 1000)
                zoom_timer = pygame.time.get_ticks()
                zoom_duration = 1000

    if nitro_active and pygame.time.get_ticks() - nitro_time > nitro_duration:
        player.deactivate_nitro()

    keys = pygame.key.get_pressed()
    player.update(keys)
    bullets.update(); enemy_bullets.update(); enemies.update()
    bosses.update(); upgrades.update(); nitro_upgrades.update()

    offset_rect = lambda r: r.move(shake_offset.x, shake_offset.y)
    for sprite in player_group: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in bullets: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in enemy_bullets: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in enemies: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in bosses: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in upgrades: screen.blit(sprite.image, offset_rect(sprite.rect))
    for sprite in nitro_upgrades: screen.blit(sprite.image, offset_rect(sprite.rect))

    screen.blit(font.render(f"Score: {player_score}", True, WHITE), (20, 20))
    screen.blit(font.render(f"Lives: {player_lives}", True, RED), (SCREEN_WIDTH - 150, 20))

    if boss_flash_timer > 0:
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash.fill(WHITE); flash.set_alpha(150)
        screen.blit(flash, (0, 0))
        boss_flash_timer -= 1

    if zoom_timer and now - zoom_timer < zoom_duration:
        scale = 1.2
        zoom_surface = pygame.transform.scale(screen, (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)))
        screen.blit(zoom_surface, (-SCREEN_WIDTH * (scale - 1) / 2, -SCREEN_HEIGHT * (scale - 1) / 2))

    if player_score >= 100 and not game_ended:
        game_ended = True
        game_over_time = pygame.time.get_ticks()

    if game_ended:
        screen.fill(BLACK)
        msg = game_over_font.render("SA VALLUTASID KOSMOST!", True, WHITE)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))
        if pygame.time.get_ticks() - game_over_time > 3000:
            game_over = True

    pygame.display.flip()
    clock.tick(60)

# Show Death Screen
if show_death_screen:
    while pygame.time.get_ticks() - death_screen_time < 4000:
        screen.blit(death_screen_img, (0, 0))
        pygame.display.flip()

pygame.quit()
exit()

