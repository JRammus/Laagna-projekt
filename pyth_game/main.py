import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Set up screen dimensions for fullscreen
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("K0SMOSE VALLUTAJAD VOL 38 ")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game variables
player_speed = 8
player_lives = 7
player_score = 0
game_over = False
boss_active = False
boost_active = False
boost_time = 0
boost_duration = 5000  # 5 seconds in milliseconds
boss_flash_timer = 0  # Boss flash effect duration
game_ended = False  # Track if the game has ended due to score
nitro_active = False
nitro_time = 0
nitro_duration = 5000  # 5 seconds in milliseconds

# Konami code detection
konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
konami_input = []
konami_code_triggered = False

# Load images
game_folder = os.getcwd()
player_image = pygame.image.load(os.path.join(game_folder, "player_ship1.png"))
player_nitro_image = pygame.image.load(os.path.join(game_folder, "player_nitro.png"))
bullet_image = pygame.image.load(os.path.join(game_folder, "bullet1.png"))
enemy_image = pygame.image.load(os.path.join(game_folder, "enemy_ship1.png"))
upgrade_image = pygame.image.load(os.path.join(game_folder, "upgrade.png"))
nitro_upgrade_image = pygame.image.load(os.path.join(game_folder, "nitro_upgrade.png"))  # New image for nitro upgrade
boss_image = pygame.image.load(os.path.join(game_folder, "boss_ship1.png"))  # Boss ship image

# Resize images
player_image = pygame.transform.scale(player_image, (84, 84))
player_nitro_image = pygame.transform.scale(player_nitro_image, (94, 94))  # nitro player image
bullet_image = pygame.transform.scale(bullet_image, (30, 60))
enemy_image = pygame.transform.scale(enemy_image, (64, 64))
boss_image = pygame.transform.scale(boss_image, (192, 192))  # Resize boss ship
upgrade_image = pygame.transform.scale(upgrade_image, (72, 72))  # 1.5x bigger
nitro_upgrade_image = pygame.transform.scale(nitro_upgrade_image, (72, 72))  # Resized nitro upgrade

# Font for displaying score and lives
font = pygame.font.Font(None, 50)
game_over_font = pygame.font.Font(None, 100)  # Font for the game end message

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.health = 100  # Initial health (this will be overridden by the Konami Code)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += player_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += player_speed

    def activate_nitro(self):
        self.image = player_nitro_image  # Change to nitro image
        global nitro_active, nitro_time
        nitro_active = True
        nitro_time = pygame.time.get_ticks()

    def deactivate_nitro(self):
        self.image = player_image  # Revert to normal image
        global nitro_active
        nitro_active = False

    def reset_health(self):
        self.health = 500  # Set health to 500


# Bullet class
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

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT // 3)))
        self.speed_x = random.choice([-4.5, 4.5])  # Increased speed by 1.5x
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x = -self.speed_x

        # Enemy shooting
        now = pygame.time.get_ticks()
        if now - self.last_shot > random.randint(1000, 3000):
            enemy_bullets.add(Bullet(self.rect.centerx, self.rect.bottom, 1))
            self.last_shot = now

# Boss class
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.speed_x = 6  
        self.health = 20  
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x = -self.speed_x

        # Boss Shooting
        now = pygame.time.get_ticks()
        if now - self.last_shot > 1000:
            enemy_bullets.add(Bullet(self.rect.centerx - 30, self.rect.bottom, 1))
            enemy_bullets.add(Bullet(self.rect.centerx + 30, self.rect.bottom, 1))
            self.last_shot = now

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False

# Upgrade class for normal upgrades
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

# nitro upgrade class
class nitroUpgrade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = nitro_upgrade_image
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -50))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Create sprite groups
player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bosses = pygame.sprite.Group()
upgrades = pygame.sprite.Group()
nitro_upgrades = pygame.sprite.Group()  # Group for nitro upgrades

# Spawn events with 1.3x increased spawn rates
enemy_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_event, int(750 * 1.3))  # Increase by 1.3x (750 * 1.3)

upgrade_spawn_event = pygame.USEREVENT + 2
pygame.time.set_timer(upgrade_spawn_event, int(10000 * 1.2))  # Decrease by 1.2x (10000 * 1.2)

# nitro upgrade spawn event with 1.7x increased spawn rate
nitro_upgrade_spawn_event = pygame.USEREVENT + 3
pygame.time.set_timer(nitro_upgrade_spawn_event, int(15000 / 2))  # Increase by 1.7x (15000 * 1.7)

# Game loop
clock = pygame.time.Clock()
while not game_over:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            # Check Konami code input
            konami_input.append(event.key)
            if len(konami_input) > len(konami_code):
                konami_input.pop(0)
            if konami_input == konami_code and not konami_code_triggered:
                player.reset_health()  # Set player health to 500
                player.activate_nitro()  # Give player permanent nitro
                boost_active = True  # Permanent upgrades after Konami code
                konami_code_triggered = True
                print("Konami Code Activated!")
                player_lives = 1000  # Set 1000 lives (not really needed but here for fun)

            if event.key == pygame.K_ESCAPE:
                game_over = True
            if event.key == pygame.K_SPACE:
                # Make the player shoot 5 bullets when Konami Code is triggered
                if konami_code_triggered:
                    for i in range(5):
                        # Fire 5 bullets from the player position
                        bullets.add(Bullet(player.rect.centerx - 15, player.rect.top, -1))
                        bullets.add(Bullet(player.rect.centerx + 15, player.rect.top, -1))
                else:
                    # Normal single bullet firing logic
                    if boost_active:
                        bullets.add(Bullet(player.rect.centerx - 15, player.rect.top, -1))
                        bullets.add(Bullet(player.rect.centerx + 15, player.rect.top, -1))
                    else:
                        bullets.add(Bullet(player.rect.centerx, player.rect.top, -1))

        elif event.type == enemy_spawn_event and not boss_active:
            enemies.add(Enemy())
        elif event.type == upgrade_spawn_event:
            upgrades.add(Upgrade())
        elif event.type == nitro_upgrade_spawn_event:
            nitro_upgrades.add(nitroUpgrade())  # nitro upgrade event

    # Spawn boss if score is high enough
    if player_score >= 30 and not boss_active:
        boss_active = True
        bosses.add(Boss())  # Add the boss to the bosses group

    # Handle nitro upgrade collection
    for nitro_upgrade in pygame.sprite.spritecollide(player, nitro_upgrades, True):
        player.activate_nitro()

    # Handle upgrade collection
    for upgrade in pygame.sprite.spritecollide(player, upgrades, True):
        if konami_code_triggered:
            boost_active = True  # Permanent upgrades after Konami code
        else:
            boost_active = True
            boost_time = pygame.time.get_ticks()
        if random.random() < 0.2:
            player_lives += 1  

    # Check if boost has expired (if Konami code isn't active)
    if not konami_code_triggered and boost_active and pygame.time.get_ticks() - boost_time > boost_duration:
        boost_active = False

    # Check if nitro has expired
    if nitro_active and pygame.time.get_ticks() - nitro_time > nitro_duration:
        player.deactivate_nitro()

    # Update player
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Update all sprites
    bullets.update()
    enemy_bullets.update()
    enemies.update()
    bosses.update()
    upgrades.update()
    nitro_upgrades.update()  # Update nitro upgrades

    # Handle bullet collisions with nitro protection
    if pygame.sprite.spritecollide(player, enemy_bullets, True) and not nitro_active:
        player_lives -= 1
        if player_lives <= 0:
            game_over = True

    enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    player_score += len(enemy_hits)

    for boss in bosses:
        if pygame.sprite.spritecollide(boss, bullets, True):  
            if boss.take_damage():  
                player_score += 10  # Add score when boss is defeated
                boss_active = False
                boss_flash_timer = 10  

    # Draw UI
    if not game_ended:
        screen.blit(font.render(f"Score: {player_score}", True, WHITE), (20, 20))
        screen.blit(font.render(f"Lives: {player_lives}", True, RED), (SCREEN_WIDTH - 150, 20))

    # End screen if the player reaches a high score
    if player_score >= 100 and not game_ended:
        game_ended = True
        game_over_time = pygame.time.get_ticks()

    if game_ended:
        screen.fill(BLACK)
        message = game_over_font.render("SA VALLUTASID KOSMOST!", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - message.get_height() // 2))
        if pygame.time.get_ticks() - game_over_time > 3000:
            game_over = True

    # Draw all sprites
    player_group.draw(screen)
    bullets.draw(screen)
    enemy_bullets.draw(screen)
    enemies.draw(screen)
    bosses.draw(screen)
    upgrades.draw(screen)
    nitro_upgrades.draw(screen)

    # Boss flash effect
    if boss_flash_timer > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surface.fill(WHITE)
        flash_surface.set_alpha(150)
        screen.blit(flash_surface, (0, 0))
        boss_flash_timer -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
exit()
