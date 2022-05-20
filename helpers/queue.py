
from enum import Enum
import random
from discord.ext import commands
from helpers.config import LYRICS_URL

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
HZ_BANDS = (20, 40, 63, 100, 150, 250, 400, 450, 630, 1000, 1600, 2500, 4000, 10000, 16000)
TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class AlreadyConnectedToChannel(commands.CommandError):
    pass


class NoVoiceChannel(commands.CommandError):
    pass


class QueueIsEmpty(commands.CommandError):
    pass


class NoTracksFound(commands.CommandError):
    pass


class PlayerIsAlreadyPaused(commands.CommandError):
    pass


class NoMoreTracks(commands.CommandError):
    pass


class NoPreviousTracks(commands.CommandError):
    pass


class InvalidRepeatMode(commands.CommandError):
    pass


class VolumeTooLow(commands.CommandError):
    pass


class VolumeTooHigh(commands.CommandError):
    pass


class MaxVolume(commands.CommandError):
    pass


class MinVolume(commands.CommandError):
    pass


class NoLyricsFound(commands.CommandError):
    pass


class InvalidEQPreset(commands.CommandError):
    pass


class NonExistentEQBand(commands.CommandError):
    pass


class EQGainOutOfBounds(commands.CommandError):
    pass


class InvalidTimeString(commands.CommandError):
    pass


class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2

class Queue:
    def __init__(self) -> None:
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE
    
    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty()
        
        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]
    
    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty()
        
        return self._queue[self.position + 1:]
    
    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty()

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty()
        
        self.position += 1
        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None
        
        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty()

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)
    
    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "one":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()
        self.position = 0