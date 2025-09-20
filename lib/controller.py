from typing import Final
from abc import ABCMeta, abstractmethod
from enum import Enum

class ButtonKind (Enum):
    Quit   = 0
    Up     = 1
    Down   = 2
    Left   = 3
    Right  = 4
    Start  = 5
    Select = 6
    A      = 7
    B      = 8
    X      = 9
    Y      = 10

class ControllerInterface (metaclass = ABCMeta):
    @abstractmethod
    def poll (self) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def shouldClose (self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def getJoystick (self) -> tuple[float, float]:
        raise NotImplementedError

    @staticmethod
    def emptyState () -> list[int]:
        return [0 for _ in ButtonKind]

class Controller:
    def __init__ (self, internal : ControllerInterface, long : int = 2):
        self.long : int = long
        self.__internal : Final[ControllerInterface] = internal
        self.__prev : list[int] = ControllerInterface.emptyState()
        self.__curr : list[int] = ControllerInterface.emptyState()

    def poll (self):
        curr = self.__internal.poll()
        self.__prev = self.__curr
        for i in range(len(curr)):
            curr[i] = 0 if curr[i] == 0 else self.__curr[i] + 1
        self.__curr = curr

    def shouldClose (self):
        return self.__internal.shouldClose() or self.isPressed(ButtonKind.Quit)

    def isPressed (self, button : ButtonKind) -> bool:
        return self.__curr[button.value] != 0

    def isShortPressed (self, button : ButtonKind) -> bool:
        return self.__prev[button.value] == 0 and self.__curr[button.value] != 0

    def isLongPressed (self, button : ButtonKind) -> bool:
        return self.__curr[button.value] > self.long

    def getButtonFrames (self, button : ButtonKind) -> int:
        return self.__curr[button.value]

    def getJoystick (self) -> tuple[float, float]:
        joystick = self.__internal.getJoystick()
        up    : Final[int] = self.getButtonFrames(ButtonKind.Up)
        down  : Final[int] = self.getButtonFrames(ButtonKind.Down)
        left  : Final[int] = self.getButtonFrames(ButtonKind.Left)
        right : Final[int] = self.getButtonFrames(ButtonKind.Right)
        def value (item : int) -> float:
            return min(item, self.long) / self.long
        h : Final[float] = value(right) - value(left)
        v : Final[float] = value(down) - value(up)
        return (h + joystick[0], v + joystick[1])
