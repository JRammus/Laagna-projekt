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

# Konami code detection
konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
konami_input = []
konami_code_triggered = False

# Load images
game_folder = os.getcwd()
player_image = pygame.image.load(os.path.join(game_folder, "player_ship.png"))
bullet_image = pygame.image.load(os.path.join(game_folder, "bullet1.png"))
enemy_image = pygame.image.load(os.path.join(game_folder, "enemy_ship.png"))
upgrade_image = pygame.image.load(os.path.join(game_folder, "upgrade.png"))
boss_image = pygame.image.load(os.path.join(game_folder, "boss_ship1.png"))  # Boss ship image

# Resize images
player_image = pygame.transform.scale(player_image, (84, 84))
bullet_image = pygame.transform.scale(bullet_image, (30, 60))
enemy_image = pygame.transform.scale(enemy_image, (64, 64))
boss_image = pygame.transform.scale(boss_image, (192, 192))  # Resize boss ship
upgrade_image = pygame.transform.scale(upgrade_image, (72, 72))  # 1.5x bigger

# Font for displaying score and lives
font = pygame.font.Font(None, 50)
game_over_font = pygame.font.Font(None, 100)  # Font for the game end message

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += player_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += player_speed

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

# Upgrade class
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

# Create sprite groups
player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bosses = pygame.sprite.Group()
upgrades = pygame.sprite.Group()

# Spawn events
enemy_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_event, 750)

upgrade_spawn_event = pygame.USEREVENT + 2
pygame.time.set_timer(upgrade_spawn_event, 10000)

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
                player_lives = 1000  # Set 1000 lives
                boost_active = True  # Make upgrades permanent
                konami_code_triggered = True
                print("Konami Code Activated!")
            
            if event.key == pygame.K_ESCAPE:
                game_over = True
            if event.key == pygame.K_SPACE:
                if boost_active:
                    bullets.add(Bullet(player.rect.centerx - 15, player.rect.top, -1))
                    bullets.add(Bullet(player.rect.centerx + 15, player.rect.top, -1))
                else:
                    bullets.add(Bullet(player.rect.centerx, player.rect.top, -1))
        elif event.type == enemy_spawn_event and not boss_active:
            enemies.add(Enemy())
        elif event.type == upgrade_spawn_event:
            upgrades.add(Upgrade())

    # Check if boss should spawn
    if player_score % 30 == 0 and player_score > 0 and not boss_active:
        boss_active = True
        bosses.add(Boss())

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

    # Update player
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Update all sprites
    bullets.update()
    enemy_bullets.update()
    enemies.update()
    bosses.update()
    upgrades.update()

    # Handle bullet collisions
    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player_lives -= 1
        if player_lives <= 0:
            game_over = True

    enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    player_score += len(enemy_hits)

    for boss in bosses:
        if pygame.sprite.spritecollide(boss, bullets, True):  
            if boss.take_damage():  
                player_score += 10
                boss_active = False
                boss_flash_timer = 10  

    # Check for score threshold to end the game
    if player_score >= 100 and not game_ended:
        game_ended = True
        game_over_time = pygame.time.get_ticks()  # Time when the game ends

    if game_ended:
        screen.fill(BLACK)  # Clear screen
        message = game_over_font.render("SA VALLUTASID KOSMOSE!", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - message.get_height() // 2))

        # Wait for 3 seconds before quitting
        if pygame.time.get_ticks() - game_over_time > 3000:
            game_over = True

    # Draw everything
    player_group.draw(screen)
    bullets.draw(screen)
    enemy_bullets.draw(screen)
    enemies.draw(screen)
    bosses.draw(screen)
    upgrades.draw(screen)

    # Flash effect
    if boss_flash_timer > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surface.fill(WHITE)
        flash_surface.set_alpha(150)
        screen.blit(flash_surface, (0, 0))
        boss_flash_timer -= 1

    # Draw UI
    if not game_ended:
        screen.blit(font.render(f"Score: {player_score}", True, WHITE), (20, 20))
        screen.blit(font.render(f"Lives: {player_lives}", True, RED), (SCREEN_WIDTH - 150, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
exit()
