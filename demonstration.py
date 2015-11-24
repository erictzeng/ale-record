from collections import namedtuple
import cPickle as pickle
import zlib

import numpy as np


class FrameBank(object):

    def __init__(self):
        self.frame_shape = None
        self.dtype = None
        self.compressed_frames = []

    def _compress_frame(self, screen_rgb):
        if self.frame_shape is None:
            self.frame_shape = screen_rgb.shape
        if self.dtype is None:
            self.dtype = screen_rgb.dtype
        if screen_rgb.shape != self.frame_shape:
            raise TypeError('expected frame of shape {}'
                            .format(self.frame_shape))
        if screen_rgb.dtype != self.dtype:
            raise TypeError('expected frame of dtype {}'.format(self.dtype))
        return zlib.compress(screen_rgb.tobytes())

    def append(self, screen_rgb):
        self.compressed_frames.append(self._compress_frame(screen_rgb))

    def __len__(self):
        return len(self.compressed_frames)

    def __getitem__(self, index):
        compressed = self.compressed_frames[index]
        decompressed = zlib.decompress(compressed)
        frame = np.frombuffer(decompressed, dtype=self.dtype)
        return frame.reshape(*self.frame_shape)

    def __setitem__(self, index, value):
        self.compressed_frames[index] = self._compress_frame(screen_rgb)

Timestep = namedtuple('Timestep', ['frame', 'action', 'reward', 'game_over'])

class Demonstration(object):

    def __init__(self):
        self.index = 0
        self.frames = FrameBank()
        self.actions = []
        self.rewards = []
        self.game_over = []

    def record_timestep(self, screen_rgb, action, reward, game_over):
        self.frames.append(screen_rgb)
        self.actions.append(action)
        self.rewards.append(reward)
        self.game_over.append(game_over)

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, index):
        return Timestep(self.frames[index], self.actions[index],
                        self.rewards[index], self.game_over[index])

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
