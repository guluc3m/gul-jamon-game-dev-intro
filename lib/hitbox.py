from abc import ABCMeta, abstractmethod
from typing import List, NoReturn, TypeAlias, Final, Self

type HitboxVisitor = HitboxVisitor

class Hitbox (metaclass = ABCMeta):
    @abstractmethod
    def accept (self, visitor : HitboxVisitor) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def collide (self, hitbox : Self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def move (self, dx : float, dy : float) -> NoReturn:
        raise NotImplementedError

    @property
    @abstractmethod
    def x (self) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def y (self) -> float:
        raise NotImplementedError

class RectHitbox (Hitbox):
    def __init__ (self, x : float, y : float, w : float, h : float):
        self.__x : float = x
        self.__y : float = y
        self.w   : float = w
        self.h   : float = h

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptRectHitbox(self)

    def collide (self, hitbox : Hitbox) -> bool:
        visitor = _RectHitboxCollideVisitor(self)
        return hitbox.accept(visitor)

    def move (self, dx : float, dy : float) -> None:
        self.__x += dx
        self.__y += dy

    @property
    def x (self) -> float:
        return self.__x

    @property
    def y (self) -> float:
        return self.__y

class CircleHitbox (Hitbox):
    def __init__ (self, cx : float, cy : float, r : float):
        self.__cx : float = cx
        self.__cy : float = cy
        self.r    : float = r

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptCircleHitbox(self)

    def move (self, dx : float, dy : float) -> None:
        self.__cx += dx
        self.__cy += dy

    def collide (self, hitbox : Hitbox) -> bool:
        visitor = _CircleHitboxCollideVisitor(self)
        return hitbox.accept(visitor)

    @property
    def x (self) -> float:
        return self.__cx - self.r

    @property
    def y (self) -> float:
        return self.__cy - self.r

    @property
    def cx (self) -> float:
        return self.__cx

    @property
    def cy (self) -> float:
        return self.__cy

class ComplexHitbox (Hitbox):
    def __init__ (self, x : float, y : float, *args : List[Hitbox]):
        self.__x     : float        = x
        self.__y     : float        = y
        self.__items : List[Hitbox] = args

    @property
    def items (self) -> List[Hitbox]:
        return self.__items

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptComplexHitbox(self)

class AABBHitbox (Hitbox):
    def __init__ (self, *args : List[Hitbox]):
        self.__items : List[Hitbox]

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptAABBHitbox(self)

class SegmentHitbox (Hitbox):
    def __init__ (self, x0 : float, y0 : float, x1 : float, y1 : float):
        self.x0 : float = min(x0, x1)
        self.y0 : float = y0
        self.x1 : float = max(x0, x1)
        self.y1 : float = y1

class HitboxVisitor (metaclass = ABCMeta):
    @abstractmethod
    def acceptRectHitbox (self, item : RectHitbox) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def acceptCircleHitbox (self, item : CircleHitbox) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def acceptComplexHitbox (self, item : ComplexHitbox) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    def acceptAABBHitbox (self, item : AABBHitbox) -> NoReturn:
        raise NotImplementedError

class _RectHitboxCollideVisitor (HitboxVisitor):
    def __init__ (self, hitbox : RectHitbox):
        self.__hitbox : Final[RectHitbox] = hitbox
    def acceptRectHitbox (self, item : RectHitbox) -> bool:
        return (self.__hitbox.x <= item.x + item.w
                and self.__hitbox.x + self.__hitbox.w >= item.x
                and self.__hitbox.y <= item.y + item.h
                and self.__hitbox.y + self.__hitbox.h >= item.y)
    def acceptAABBHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)
    def acceptComplexHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)
    def acceptCircleHitbox (self, item : AABBHitbox) -> bool:
        if (self.__hitbox.x <= item.cx <= self.__hitbox.x + self.__hitbox.w and
            self.__hitbox.y <= item.cy <= self.__hitbox.y + self.__hitbox.h):
            return True

class _CircleHitboxCollideVisitor (HitboxVisitor):
    def __init__ (self, hitbox : CircleHitbox):
        self.__hitbox : Final[CircleHitbox] = hitbox
    def acceptRectHitbox (self, item : RectHitbox) -> bool:
        raise NotImplementedError
    def acceptAABBHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)
    def acceptComplexHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)
    def acceptCircleHitbox (self, item : AABBHitbox) -> bool:
        raise NotImplementedError
