import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 64
ENEMY_SIZE = 64
BULLET_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SPEED = 7
BULLET_SPEED = 10
ENEMY_SPEED = 4
ENEMY_BULLET_SPEED = 6
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
SHOOT_ENEMY_BULLET_EVENT = pygame.USEREVENT + 2

# Load images
background = pygame.image.load("spacebackground.jpg")
player_img = pygame.image.load("player.png")
enemy_img = pygame.image.load("enemy.png")
bullet_img = pygame.image.load("bullet.png")
enemy_bullet_img = pygame.image.load("enemy_bullet.png")
ENEMY_BULLET_SIZE = 52

# Scale images to the appropriate size
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
enemy_img = pygame.transform.scale(enemy_img, (ENEMY_SIZE, ENEMY_SIZE))
bullet_img = pygame.transform.scale(bullet_img, (BULLET_SIZE, BULLET_SIZE))
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (ENEMY_BULLET_SIZE, ENEMY_BULLET_SIZE))

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Shooter")

# Font setup
font = pygame.font.Font(None, 36)

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.rect = enemy_img.get_rect(topleft=(x, y))
        self.speed = ENEMY_SPEED

    def move_towards_player(self, player_rect):
        # Simplified movement towards player
        if self.rect.centerx < player_rect.centerx:
            self.rect.x += self.speed
        elif self.rect.centerx > player_rect.centerx:
            self.rect.x -= self.speed
        if self.rect.centery < player_rect.centery:
            self.rect.y += self.speed
        elif self.rect.centery > player_rect.centery:
            self.rect.y -= self.speed

# Enemy bullet class
class EnemyBullet:
    def __init__(self, x, y, direction):
        self.rect = enemy_bullet_img.get_rect(center=(x, y))
        self.direction = direction

    def move(self):
        self.rect.move_ip(self.direction[0] * ENEMY_BULLET_SPEED, self.direction[1] * ENEMY_BULLET_SPEED)

# Spawn enemy function
def spawn_enemy():
    x_pos = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
    enemy = Enemy(x_pos, -ENEMY_SIZE)
    enemies.append(enemy)

# Shoot enemy bullet function
def shoot_enemy_bullet():
    if enemies:
        enemy = random.choice(enemies)
        direction = ((player_rect.centerx - enemy.rect.centerx), (player_rect.centery - enemy.rect.centery))
        magnitude = (direction[0]**2 + direction[1]**2) ** 0.5
        direction = (direction[0] / magnitude, direction[1] / magnitude)
        enemy_bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.centery, direction)
        enemy_bullets.append(enemy_bullet)

# Display Game Over screen
def game_over_screen():
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER", True, WHITE)
    restart_text = font.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Game loop
def main_game():
    global bullets, enemies, enemy_bullets, player_rect, score, level
    player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * PLAYER_SIZE))
    bullets = []
    enemies = []
    enemy_bullets = []
    score = 0
    level = 1

    clock = pygame.time.Clock()
    running = True

    # Spawn enemy timer
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1000)
    pygame.time.set_timer(SHOOT_ENEMY_BULLET_EVENT, 1500)

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == SPAWN_ENEMY_EVENT:
                spawn_enemy()
            elif event.type == SHOOT_ENEMY_BULLET_EVENT:
                shoot_enemy_bullet()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.move_ip(-PLAYER_SPEED, 0)
        if keys[pygame.K_RIGHT] and player_rect.right < SCREEN_WIDTH:
            player_rect.move_ip(PLAYER_SPEED, 0)
        if keys[pygame.K_SPACE]:
            bullet_rect = bullet_img.get_rect(midbottom=player_rect.midtop)
            bullets.append(bullet_rect)

        # Bullet movement
        for bullet in bullets[:]:
            bullet.move_ip(0, -BULLET_SPEED)
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Enemy movement towards player
        for enemy in enemies:
            enemy.move_towards_player(player_rect)
            if enemy.rect.colliderect(player_rect):
                running = False  # Game over if enemy collides with player

        # Enemy bullet movement
        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet.move()
            if enemy_bullet.rect.colliderect(player_rect):
                running = False  # Game over if enemy bullet hits player
            if enemy_bullet.rect.top > SCREEN_HEIGHT:
                enemy_bullets.remove(enemy_bullet)

        # Collision detection between bullets and enemies
        enemies_to_remove = []
        bullets_to_remove = []
        for bullet in bullets:
            for enemy in enemies:
                if bullet.colliderect(enemy.rect):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    score += 1

        # Remove collided bullets and enemies
        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)

        # Increase difficulty for level 2
        if score >= 20 and level == 1:
            level = 2
            pygame.time.set_timer(SPAWN_ENEMY_EVENT, 500)  # Increase spawn rate


        if score >= 80 and level == 2:
            level = 3
            pygame.time.set_timer(SPAWN_ENEMY_EVENT, 400)  # Increase spawn rate

        if score >= 150 and level == 3:
            level = 4
            pygame.time.set_timer(SPAWN_ENEMY_EVENT, 250)  # Increase spawn rate

        if score >= 250 and level == 4:
            level = 5
            pygame.time.set_timer(SPAWN_ENEMY_EVENT, 100)  # Increase spawn rate

        # Drawing
        screen.blit(background, (0, 0))
        screen.blit(player_img, player_rect.topleft)
        for bullet in bullets:
            screen.blit(bullet_img, bullet.topleft)
        for enemy in enemies:
            screen.blit(enemy_img, enemy.rect.topleft)
        for enemy_bullet in enemy_bullets:
            screen.blit(enemy_bullet_img, enemy_bullet.rect.topleft)

        # Display score and level
        score_text = font.render(f"Score: {score}", True, BLACK)
        level_text = font.render(f"Level: {level}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

        # Update display
        pygame.display.flip()
        clock.tick(60)

    # Display Game Over screen
    game_over_screen()

# Main game loop
while True:
    main_game()
