import pygame, random
from pygame.locals import *
pygame.mixer.pre_init()
pygame.init()


clock = pygame.time.Clock()
FPS = 60

size = [600, 400]

screen = pygame.display.set_mode(size)

display = pygame.Surface((300, 200))

true_scroll = [0, 0]

CHUNK_SIZE = 8

def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0
            if target_y > 10:
                tile_type = 2
            if target_y == 10:
                tile_type = 1
            if target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])

    return chunk_data

game_map = {}

grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')
plant_img = pygame.image.load('plant.png')
plant_img.set_colorkey((255,255,255))
tile_index = {1:grass_img,
              2:dirt_img,
              3:plant_img}


player_img = pygame.image.load('player_animations/idle/idle_0.png')
player_img.set_colorkey((255,255,255))
player_rect = pygame.Rect(100, 0, 5, 13)

background_objects = [[0.25, [120, 10, 70, 400]],
                      [0.25, [280, 30, 40, 400]],
                      [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]],
                      [0.5, [300, 80, 120, 400]]]




moving_right = moving_left = False
vertical_momentum = 0
air_timer = 0

pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound('jump.wav')


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top':False, 'bottom':False, 'left':False, 'right':False}

    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        if movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True


    return rect, collision_types


global animation_frames
animation_frames = {}


def load_animation(path, frame_duration):
    global animation_frames
    animation_name = path.split('/')[-1] #run
    animation_frame_data = []
    n = 0
    for frame in frame_duration: #7 7
        animation_frame_id = animation_name + '_' + str(n) #run_0
        img = path + '/' + animation_frame_id + '.png'
        animation_img = pygame.image.load(img).convert()
        animation_img.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_img.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

animation_database = {}
animation_database['run'] = load_animation('player_animations/run', [7,7])
animation_database['idle'] = load_animation('player_animations/idle', [7,7,48])

player_action = 'idle'
player_frame = 0
player_flip = False

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return  action_var, frame



grass_sounds = [pygame.mixer.Sound('grass_0.wav'), pygame.mixer.Sound('grass_1.wav')]
grass_sounds[0].set_volume(0.1)
grass_sounds[1].set_volume(0.1)
grass_sound_timer = 0

while True:
    true_scroll[0] += (player_rect.x - true_scroll[0] - 152)/16
    true_scroll[1] += (player_rect.y - true_scroll[1] - 106)/16
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])


    display.fill(((146, 244, 255)))
    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0],
                               background_object[1][2], background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)


    tile_rects = []

    for y in range(3):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x, target_y)

            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]], (tile[0][0]*16-scroll[0],
                                                   tile[0][1]*16-scroll[1]))
                if tile[1] in [1,2]:
                    tile_rects.append(pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16))




    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3


    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action, player_frame = change_action(player_action, player_frame, 'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action, player_frame = change_action(player_action, player_frame, 'run')



    player_rect, collisions= move(player_rect, player_movement, tile_rects)
    if grass_sound_timer > 0:
        grass_sound_timer -= 1
    if collisions['bottom']:
        air_timer = 0
        vertical_momentum = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 50
                random.choice(grass_sounds).play()

    else:
        air_timer += 1

    if collisions['top']:
        vertical_momentum = 0
    #run_0 run_0 run_0 run_0 run_0 run_0 run_0 run_1 run_1 run_1 run_1 run_1 run_1 run_1
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip,False),
                 (player_rect.x - scroll[0], player_rect.y - scroll[1]))


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    vertical_momentum = -5

        if event.type == KEYUP:
            if event.key == K_LEFT:
                moving_left = False
            if event.key == K_RIGHT:
                moving_right = False



    screen.blit(pygame.transform.scale(display, size), (0,0))
    pygame.display.update()
    clock.tick(FPS)