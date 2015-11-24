#!/usr/bin/env python
import time

import ale_python_interface as ALE
import click
import pygame
import pygame.locals as pl

from demonstration import Demonstration

keys = [pl.K_SPACE, pl.K_UP, pl.K_RIGHT, pl.K_LEFT, pl.K_DOWN]

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


def keystates_to_ale_action(keystates):
    keystates = dict(keystates)
    if keystates[pl.K_UP] and keystates[pl.K_DOWN]:
        keystates[pl.K_UP] = False
        keystates[pl.K_DOWN] = False
    if keystates[pl.K_LEFT] and keystates[pl.K_RIGHT]:
        keystates[pl.K_LEFT] = False
        keystates[pl.K_RIGHT] = False
    bitvec = sum(2 ** i if keystates[key] else 0 for i, key in enumerate(keys))
    assert bitvec in mapping
    return mapping[bitvec]


def update_keystates(keystates):
    events = pygame.event.get()
    for event in events:
        if hasattr(event, 'key') and event.key in keys:
            if event.type == pygame.KEYDOWN:
                keystates[event.key] = True
            elif event.type == pygame.KEYUP:
                keystates[event.key] = False

@click.group()
def cli():
    pygame.init()

@cli.command(name='new')
@click.argument('rom', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--frames', default=60 * 60 * 30)
@click.option('--seed', default=123)
def record_new(rom, output, frames, seed):
    ale = ALE.ALEInterface()
    ale.setInt('random_seed', seed)
    ale.setBool('display_screen', True)
    ale.loadROM(rom)
    demo = Demonstration(rom)
    record(ale, demo, output, frames)

@cli.command(name='resume')
@click.argument('partial_demo', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--frames', default=60 * 60 * 30)
@click.option('--rom', default=None)
def resume(partial_demo, output, frames, rom):
    demo = Demonstration.load(partial_demo)
    ale = ALE.ALEInterface()
    ale.setBool('display_screen', True)
    if not rom:
        ale.loadROM(demo.rom)
    else:
        ale.loadROM(rom)
    demo.reset_to_latest_snapshot(ale)
    record(ale, demo, output, frames)

def record(ale, demo, output, num_frames):
    keystates = {key: False for key in keys}
    score = 0
    try:
        while len(demo) < num_frames:
            if len(demo) % demo.snapshot_interval == 0:
                demo.snapshot(ale)
            update_keystates(keystates)
            action = keystates_to_ale_action(keystates)
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
            demo.record_timestep(ale.getScreenRGB(), action, reward, game_over)
    except KeyboardInterrupt:
        pass
    finally:
        demo.snapshot(ale)
        demo.save(output)

if __name__ == '__main__':
    cli()
