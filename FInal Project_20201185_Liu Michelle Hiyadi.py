import pygame
import random
import math
from os import path

img_dir = path.join(path.dirname(__file__), 'image')
snd_dir = path.join(path.dirname(__file__), 'sound')

WIDTH = 1300
HEIGHT = 512
FPS = 60
POWERUP_TIME: 5000
MAX_EAGLES = 3

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Last Fish")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('Georgia')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    if len(mobs) < MAX_EAGLES:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.transform.scale(player_standing, (144, 131)), pygame.transform.scale(player_standing2, (144, 131))]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = 100
        self.rect.bottom = 512
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.vel_y = 10
        self.jump = False
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.death_timer = 0

    def update(self):
        # timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = 100
            self.rect.bottom = 512


        self.speedx = 0
        self.speedy = 0

        keystate = pygame.key.get_pressed()

        if self.jump is False and keystate[pygame.K_UP]:
            self.jump = True
        if self.jump is True:
            self.rect.bottom -= self.vel_y*6
            self.vel_y -= 1
            if self.vel_y < -10:
                self.jump = False
                self.vel_y = 10

        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
  
        if keystate[pygame.K_SPACE]:
            self.shoot()

        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        
        self.image = self.images[self.index]
        
        self.rect.x += self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.y += self.speedy

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.death_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = enemy_img
        self.image = self.image_orig.copy()
        self.rect = self.image_orig.get_rect()
        self.width = random.randint(20,100)
        self.height = random.randint(100,400)
        self.rect.x = WIDTH
        self.rect.y = random.randint(0, HEIGHT - self.height)
        self.speed = random.randint(5,6)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = WIDTH
            self.rect.y = self.height

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y - 30
        self.rect.centerx = x
        self.speedx = 10

    def update(self):
        self.rect.x += self.speedx
        # kill if it moves off the top of the screen
        if self.rect.left < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "The Last Fish", 70, WIDTH / 2, HEIGHT / 8.5)
    draw_text(screen, "UP to JUMP, LEFT and RIGHT to move, SPACE to shoot fireballs", 18,
              WIDTH / 2, HEIGHT / 3.5)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text(screen, "20201185 - Liu Michelle Hiyadi", 18, WIDTH / 2, HEIGHT / 2)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Load all game graphics
background = pygame.image.load(path.join(img_dir, "thelastfishbg.png")).convert()
background_width = background.get_width()
background_rect = background.get_rect()
scroll = 0
tiles = math.ceil(WIDTH / background_width) + 1

player_standing = pygame.image.load(path.join(img_dir, "fish1.png"))
player_standing2 = pygame.image.load(path.join(img_dir, "fish2.png"))
player_mini_img = pygame.image.load(path.join(img_dir, "Heart.png"))
player_mini_img = pygame.transform.scale(player_mini_img, (34, 34))

bullet_img = pygame.image.load(path.join(img_dir, "Fireball1.png"))
enemy_img = pygame.image.load(path.join(img_dir, "eaglebig.png"))
enemy_img = pygame.transform.scale(enemy_img, (300, 206))
enemy_img.set_colorkey(BLACK)
enemies_images = pygame.sprite.Group()


explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []

for i in range(2):
    filename = 'fire{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename))
    img_lg = pygame.transform.scale(img, (300, 206))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (300, 206))
    explosion_anim['sm'].append(img_sm)

for i in range (3):
    filename = 'dead{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename))
    explosion_anim['player'].append(img)
   
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'heartsm.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'firesm.png')).convert()


# Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'fireball.mp3'))
expl_sounds = []
for snd in ['screeching.mp3']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'swoosh.mp3'))
pygame.mixer.music.load(path.join(snd_dir, 'Enchantedvalley.mp3'))
pygame.mixer.music.set_volume(0.4)
              
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
   newmob()

score = 0
pygame.mixer.music.play(loops=-1)
# Game loop
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0

    clock.tick(FPS)
    
    for i in range(0, tiles):
        screen.blit(background, (i * background_width + scroll, 0))

    scroll -= 2

    if abs(scroll) > background_width:
        scroll = 0 

    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    # check to see if player hit a powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            pass

    # if the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        running = False

    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()
