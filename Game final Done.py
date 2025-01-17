import pygame
import math
import random
import os
import PySimpleGUI as sg

# PySimpleGUI akna seadistamine/pysimpleGUI screen
def main_menu():
    layout = [
        [sg.Text('Tere tulemast Kosmoselennuki mängu!', font=('Helvetica', 20))],
        [sg.Button('Alusta mängu')]
    ]
    window = sg.Window('Mängu Menüü', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Välju':
            window.close()
            return False
        elif event == 'Alusta mängu':
            window.close()
            return True

pygame.init()

# ekraani mõõdud/Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# värvid/Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Kell ja font/Clock and font
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# top skoori fail/File for storing top score
TOP_SCORE_FILE = "top_score.txt"

# laadida top skoori fail/Function to load the top score from a file
def load_top_score():
    if os.path.exists(TOP_SCORE_FILE):
        with open(TOP_SCORE_FILE, "r") as file:
            try:
                return int(file.read())
            except ValueError:
                return 0
    return 0

# top skoori save/Function to save the top score to a file
def save_top_score(score):
    with open(TOP_SCORE_FILE, "w") as file:
        file.write(str(score))

# Kosmoselaeva klass/Spaceship class
class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 5
        self.size = 20

    def draw(self):
        tip_x = self.x + math.cos(math.radians(self.angle)) * self.size
        tip_y = self.y - math.sin(math.radians(self.angle)) * self.size
        left_x = self.x + math.cos(math.radians(self.angle + 120)) * self.size // 1.5
        left_y = self.y - math.sin(math.radians(self.angle + 120)) * self.size // 1.5
        right_x = self.x + math.cos(math.radians(self.angle - 120)) * self.size // 1.5
        right_y = self.y - math.sin(math.radians(self.angle - 120)) * self.size // 1.5
        pygame.draw.polygon(screen, BLUE, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

    def move(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

# Kuuli klass/Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.radius = 5

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

# Vaenlase klass/Enemy class
class Enemy:
    def __init__(self):
        self.size = random.randint(20, 40)
        self.x, self.y = self.random_spawn()
        self.speed = random.uniform(1, 3)
        self.angle = math.degrees(math.atan2(HEIGHT // 2 - self.y, WIDTH // 2 - self.x))

    def random_spawn(self):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return random.randint(0, WIDTH), 0
        elif side == "bottom":
            return random.randint(0, WIDTH), HEIGHT
        elif side == "left":
            return 0, random.randint(0, HEIGHT)
        else:
            return WIDTH, random.randint(0, HEIGHT)

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))

# Mängu funktsioon/game function
def game():
    top_score = load_top_score() # laadida top skoor/Load the top score from the file
    spaceship = Spaceship()
    bullets = []
    enemies = []
    spawn_timer = 0
    shoot_timer = 0
    score = 0
    running = True

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - spaceship.x
        dy = mouse_y - spaceship.y
        spaceship.angle = math.degrees(math.atan2(-dy, dx))

        spaceship.move(keys)

        shoot_timer += clock.get_time()
        if pygame.mouse.get_pressed()[0] and shoot_timer > 300:
            tip_x = spaceship.x + math.cos(math.radians(spaceship.angle)) * spaceship.size
            tip_y = spaceship.y - math.sin(math.radians(spaceship.angle)) * spaceship.size
            bullets.append(Bullet(tip_x, tip_y, spaceship.angle))
            shoot_timer = 0

        spawn_timer += clock.get_time()
        if spawn_timer > max(500 - score * 10, 100):
            enemies.append(Enemy())
            spawn_timer = 0

        for bullet in bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
            bullet.draw()

        for enemy in enemies[:]:
            enemy.update()
            if enemy.x < -enemy.size or enemy.x > WIDTH + enemy.size or enemy.y < -enemy.size or enemy.y > HEIGHT + enemy.size:
                enemies.remove(enemy)
            enemy.draw()

            for bullet in bullets[:]:
                if pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size).collidepoint(bullet.x, bullet.y):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1

            if pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size).colliderect(
                pygame.Rect(spaceship.x - spaceship.size, spaceship.y - spaceship.size, spaceship.size * 2, spaceship.size * 2)):
                return game_over(score, top_score)

        spaceship.draw()

        score_text = font.render(f"Skoor: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        top_score_text = font.render(f"Parim skoor: {top_score}", True, WHITE)
        screen.blit(top_score_text, (10, 50))

        pygame.display.flip()
        clock.tick(60)

# Mängu lõpp/ Game over
def game_over(score, top_score):
    if score > top_score:
        top_score = score
        save_top_score(top_score) # salvestada top skoor faili/Save new top score to the file

    screen.fill(BLACK)
    game_over_text = font.render("Mäng läbi!", True, RED)
    score_text = font.render(f"Skoor: {score}", True, WHITE)
    play_again_text = font.render("Vajuta R uuesti mängimiseks või ESC lahkumiseks", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3 + 50))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 3 + 100))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False

# Mängu algus/ game start
if main_menu():
    game()