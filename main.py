import pygame as pg
from sys import exit
from random import randint, choice

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        player_walk_1 = pg.image.load('graphics/player/player_walk_1.png').convert_alpha()
        player_walk_2 = pg.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_stand = pg.image.load('graphics/player/player_stand.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_orientation = 'r'
        self.player_index = 0
        self.player_jump = pg.image.load('graphics/player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(bottomleft =  (50,300))
        self.gravity = 0

        self.jump_sound = pg.mixer.Sound('audio/audio_jump.mp3')
        self.jump_sound.set_volume(0.1)

    def player_input(self, jump = False):
        keys = pg.key.get_pressed()

        # Jump
        if jump and self.rect.bottom >= 300:
            self.gravity = -15
            self.jump_sound.play()
        elif (keys[pg.K_SPACE] or keys[pg.K_UP]) and self.gravity < 0: 
            self.gravity -= 1
        
        # Move right
        if keys[pg.K_RIGHT]:
            self.player_orientation = 'right'
            if self.rect.right < 800:
                self.rect.x += 7
        
        # Move left
        if keys[pg.K_LEFT]:
            self.player_orientation = 'left'
            if self.rect.left > 0:
                self.rect.x -= 7

    def apply_gravity(self):
        self.gravity += 1.5
        self.rect.y += self.gravity
        if self.rect.bottom >= 300: self.rect.bottom = 300

    def restart(self):
        self.gravity = 0
        self.rect.bottomleft = (50,300)

    def animation_state(self):
        
        keys = pg.key.get_pressed()
        
        # Jump animation
        if self.rect.bottom < 300: 
            if self.player_orientation == 'left':
                self.image = pg.transform.flip(self.player_jump, True, False)
            else: 
                self.image = self.player_jump
        
        # Move right animation
        elif keys[pg.K_RIGHT]:
            self.player_index += 0.05
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
        
        # Move left animation
        elif keys[pg.K_LEFT]:
            self.player_index += 0.05
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = pg.transform.flip(self.player_walk[int(self.player_index)], True, False)

        # Stand animation
        else:
            self.image = self.player_stand

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pg.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        self.type = type

        if self.type == 'fly':
            fly_1 = pg.image.load('graphics/Fly/Fly1.png').convert_alpha()
            fly_2 = pg.image.load('graphics/Fly/Fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = randint(150, 220)

        else:
            snail_1 = pg.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pg.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300
        
        self.animation_index = 0
        
        self.image = self.frames[self.animation_index] 
        self.rect = self.image.get_rect(midbottom = (randint(900, 1100), y_pos))

    def animation_state(self):
        if self.type == 'fly':
            self.animation_index += 0.1
        else: 
            self.animation_index += 0.02
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.right < 0:
            self.kill()

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy

def display_score():
    current_time = (pg.time.get_ticks() - start_time)//100
    score_surf = test_font.render(f'{current_time}', False, (64,64,64))
    score_rect = score_surf.get_rect(topright = (750,50))
    screen.blit(score_surf,score_rect)
    return current_time

def collision_sprite():
    if pg.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else: return True


pg.init()
screen = pg.display.set_mode((800, 400))
pg.display.set_caption('Runner')
clock = pg.time.Clock()
game_active = False
start_time = 0
score = 0
bg_music = pg.mixer.Sound('audio/music.wav')
bg_music.set_volume(0.5)
bg_music.play(loops = -1)

player = pg.sprite.GroupSingle()
player.add(Player())

obstacle_group = pg.sprite.Group()

# Intro screen
test_font = pg.font.Font('fonts/Pixeltype.ttf', 50)
title_surf = test_font.render('Tutorial Game', False, 'White')
title_rect = title_surf.get_rect(center = (400,50))
instruct_message = test_font.render('Press space to start', False, 'White')
instruct_rect = instruct_message.get_rect(center = (400,350))

# Background
sky_surface = pg.image.load('graphics/Sky.png').convert()
ground_surface = pg.image.load('graphics/ground.png').convert()

# Gameover screen
gameover_surf = test_font.render('Game Over', False, 'white')
gameover_rect = gameover_surf.get_rect(center = (400,50))
player_stand = pg.image.load('./graphics/Player/player_stand.png').convert_alpha()
player_stand = pg.transform.rotozoom(player_stand, 0, 1.7)
player_stand_rect = player_stand.get_rect(center = (400,200))

# Timers
obstacle_timer = pg.USEREVENT + 1
pg.time.set_timer(obstacle_timer, 1500)

snail_animation_timer = pg.USEREVENT + 2
pg.time.set_timer(snail_animation_timer, 400)

fly_animation_timer = pg.USEREVENT + 3
pg.time.set_timer(fly_animation_timer, 150)

# Delay in jump input in air if input within 0.1s of touching the ground
jump_delay_timer = -1


while True:

    # Event loop
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            pg.quit()
            exit()

        if game_active:
            # Obstacle generator
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail'])))
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    player.sprite.player_input(jump=True)
                    jump_delay_timer = pg.time.get_ticks()

        else:
        # Restart game
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    player.sprite.restart()
                    game_active = True
                    start_time = pg.time.get_ticks()

    if game_active:

        if player.sprite.rect.bottom >= 300:
            if jump_delay_timer >=0 and pg.time.get_ticks() - jump_delay_timer < 100:
                player.sprite.player_input(jump=True)
        
        screen.blit(sky_surface,(0,0))
        screen.blit(ground_surface,(0,300))

        score = display_score()
        
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        game_active = collision_sprite()
        
    else:
        screen.fill((94,129,162))
        screen.blit(player_stand, player_stand_rect)
        score_message = test_font.render(f'{score}', False, 'white')
        score_rect = score_message.get_rect(center = (400, 350))
        
        if score == 0: 
            screen.blit(title_surf,title_rect)
            screen.blit(instruct_message,instruct_rect)
        else: 
            screen.blit(gameover_surf,gameover_rect)
            screen.blit(score_message,score_rect)

    pg.display.update()
    clock.tick(60)