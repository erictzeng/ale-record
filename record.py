import ale_python_interface as ALE
import pygame
import pygame.locals as pl
import time

ale = ALE.ALEInterface()
ale.setInt('random_seed', 123)
pygame.init()
ale.setBool('display_screen', True)
ale.loadROM('space_invaders.bin')
print pygame.display.Info()

keys = [pl.K_SPACE, pl.K_UP, pl.K_RIGHT, pl.K_LEFT, pl.K_DOWN]
keystates = {key: False for key in keys}

mapping = {
    # dlruf
    0b00000: 0,
    0b00001: 1,
    0b00010: 2,
    0b00100: 3,
    0b01000: 4,
    0b10000: 5,
    0b00110: 6,
    0b01010: 7,
    0b10100: 8,
    0b11000: 9,
    0b00011: 10,
    0b00101: 11,
    0b01001: 12,
    0b10001: 13,
    0b00111: 14,
    0b01011: 15,
    0b10101: 16,
    0b11001: 17
    }

def keystate_to_ale_action(keystate):
    keystate = dict(keystate)
    if keystate[pl.K_UP] and keystate[pl.K_DOWN]:
        keystate[pl.K_UP] = False
        keystate[pl.K_DOWN] = False
    if keystate[pl.K_LEFT] and keystate[pl.K_RIGHT]:
        keystate[pl.K_LEFT] = False
        keystate[pl.K_RIGHT] = False
    bitvec = sum(2**i if keystate[key] else 0 for i, key in enumerate(keys))
    assert bitvec in mapping
    return mapping[bitvec]
        

score = 0
record = []
while True:
    events = pygame.event.get()
    for event in events:
        if hasattr(event, 'key') and event.key in keys:
            if event.type == pygame.KEYDOWN:
                keystates[event.key] = True
            elif event.type == pygame.KEYUP:
                keystates[event.key] = False
    action = keystate_to_ale_action(keystates)
    reward = ale.act(action)
    score += reward
    game_over = False
    if ale.game_over():
        print 'game over, score: {}'.format(score)
        print 'restarting in 5 seconds'
        score = 0
        game_over = True
        time.sleep(5)
        ale.reset_game()
    record.append({'screen': ale.getScreenRGB(), 'reward': reward, 'action': action, 'game_over': game_over})
