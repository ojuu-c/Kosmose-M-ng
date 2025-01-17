import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
FPS = 60

spaceship_img = pygame.Surface((50, 40), pygame.SRCALPHA)
pygame.draw.polygon(spaceship_img, BLUE, [(25, 0), (50, 40), (0, 40)])
spaceship_pos = [WIDTH // 2, HEIGHT // 2]
spaceship_speed = 5
spaceship_angle = 0

bullets = []
bullet_speed = 10

enemies = []
enemy_spawn_rate = 30
enemy_speed = 2

score = 0
font = pygame.font.SysFont(None, 36)

def draw_text(text, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

running = True
spawn_timer = 0
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if keys[pygame.K_w]:
        spaceship_pos[1] -= spaceship_speed
    if keys[pygame.K_s]:
        spaceship_pos[1] += spaceship_speed
    if keys[pygame.K_a]:
        spaceship_pos[0] -= spaceship_speed
    if keys[pygame.K_d]:
        spaceship_pos[0] += spaceship_speed

    dx, dy = mouse_x - spaceship_pos[0], mouse_y - spaceship_pos[1]
    spaceship_angle = math.degrees(math.atan2(-dy, dx))

    if pygame.mouse.get_pressed()[0]:
        bullets.append([spaceship_pos[0], spaceship_pos[1], spaceship_angle])

    for bullet in bullets[:]:
        bullet[0] += bullet_speed * math.cos(math.radians(bullet[2]))
        bullet[1] -= bullet_speed * math.sin(math.radians(bullet[2]))

        if not (0 <= bullet[0] <= WIDTH and 0 <= bullet[1] <= HEIGHT):
            bullets.remove(bullet)

    spawn_timer += 1
    if spawn_timer >= enemy_spawn_rate:
        spawn_timer = 0
        enemies.append([random.randint(0, WIDTH), 0, enemy_speed])

    for enemy in enemies[:]:
        enemy[1] += enemy[2]

        if enemy[1] > HEIGHT:
            enemies.remove(enemy)

    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if math.hypot(bullet[0] - enemy[0], bullet[1] - enemy[1]) < 20:
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                enemy_speed += 0.1
                break

    rotated_ship = pygame.transform.rotate(spaceship_img, spaceship_angle)
    rect = rotated_ship.get_rect(center=spaceship_pos)
    screen.blit(rotated_ship, rect.topleft)

    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), 5)

    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0] - 10, enemy[1] - 10, 20, 20))

    draw_text(f"Score: {score}", WHITE, 10, 10)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()