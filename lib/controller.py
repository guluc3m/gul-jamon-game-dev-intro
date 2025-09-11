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

class Controller (metaclass = ABCMeta):
    @abstractmethod
    def poll (self) -> None:
        raise NotImplementedError

    @abstractmethod
    def shouldClose (self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def getButtonPressedFrames (self, button : ButtonKind) -> int:
        raise NotImplementedError

    @abstractmethod
    def getJoystick (self) -> tuple[float, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def longPressedFrames (self) -> int:
        raise NotImplementedError

    def isLongPressed (self, button : ButtonKind) -> bool:
        return self.getButtonPressedFrames(button) > self.longPressedFrames

    def isPressed (self, button : ButtonKind) -> bool:
        return self.getButtonPressedFrames(button) > 0
