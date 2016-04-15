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

    def reset_to_timestep(self, t):
        del self.compressed_frames[t:]

Timestep = namedtuple('Timestep', ['frame', 'action', 'reward', 'game_over'])

class Demonstration(object):

    snapshot_interval = 1000

    def __init__(self, rom, action_set):
        self.rom = rom
        self.action_set = action_set
        self.frames = FrameBank()
        self.actions = []
        self.rewards = []
        self.game_over = []
        self.snapshots = {}

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

    def snapshot(self, ale):
        state_ptr = ale.cloneSystemState()
        self.snapshots[len(self)] = ale.encodeState(state_ptr)
        ale.deleteState(state_ptr)

    def reset_to_timestep(self, t):
        for key in self.snapshots.keys():
            if key > t:
                del self.snapshots[key]
        self.frames.reset_to_timestep(t)
        del self.actions[t:]
        del self.rewards[t:]
        del self.game_over[t:]
        
    def reset_to_latest_snapshot(self, ale):
        latest = max(self.snapshots.keys())
        self.reset_to_timestep(latest)
        state_enc = self.snapshots[latest]
        state_ptr = ale.decodeState(state_enc)
        ale.restoreSystemState(state_ptr)
        ale.deleteState(state_ptr)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
