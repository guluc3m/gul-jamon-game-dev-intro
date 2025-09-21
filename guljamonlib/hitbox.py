from abc import ABCMeta, abstractmethod
from typing import List, NoReturn, TypeAlias, Final, Self

type HitboxVisitor = HitboxVisitor
type Point = tuple[float, float]
type Vector = tuple[float, float]

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

class SegmentHitbox (Hitbox):
    def __init__ (self, x0 : float, y0 : float, x1 : float, y1 : float):
        self.__x0 : float = min(x0, x1)
        self.__y0 : float = y0
        self.__x1 : float = max(x0, x1)
        self.__y1 : float = y1

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptSegmentHitbox(self)

    def collide (self, hitbox : Hitbox) -> bool:
        return True

    def move (self, dx : float, dy : float) -> None:
        self.__x0 += dx
        self.__y0 += dy
        self.__x1 += dx
        self.__y1 += dy

    def __ccw(self, a : Point, b : Point, c : Point) -> bool:
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    def __intersect(self, a : Point, b : Point, c : Point, d : Point) -> bool:
        return (self.__ccw(a,c,d) != self.__ccw(b,c,d) and
                self.__ccw(a,b,c) != self.__ccw(a,b,d))

    def intersects (self, left : Point, right : Point) -> bool:
        # https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
        return self.__intersect((self.__x0, self.__y0), (self.__x1, self.__y1),
                                left, right)

    @property
    def x (self) -> float: return self.__x0
    @property
    def y (self) -> float: return self.__y0
    @property
    def x0 (self) -> float: return self.__x0
    @property
    def y0 (self) -> float: return self.__y0
    @property
    def x1 (self) -> float: return self.__x1
    @property
    def y1 (self) -> float: return self.__y1

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
    def collideCircle (self, other : Self) -> bool:
        return ((other.cx - self.cx) ** 2 + (other.cy - self.cy) ** 2
                < (other.r + self.r) ** 2)
    def collideSegment (self, item : SegmentHitbox) -> bool:
        # https://stackoverflow.com/questions/1073336/circle-line-segment-collision-detection-algorithm
        def dot (a : Vector, b : Vector) -> float:
            return a[0] * b[0] + a[1] * b[1]

        E : Final[Point] = (item.x0, item.y0)
        L : Final[Point] = (item.x1, item.y1)
        C : Final[Point] = (self.cx, self.cy)
        r : Final[float] = self.r
        if (self.contains(E) or self.contains(L)):
            return True
        d : Final[Vector] = (L[0] - E[0], L[1] - E[1])
        f : Final[Vector] = (E[0] - C[0], E[1] - C[1])
        a : Final[float]  = dot(d, d)
        b : Final[float]  = 2 * dot(f, d)
        c : Final[float]  = dot(f, f) - r * r

        discriminant : float = b * b - 4 * a * c
        if (discriminant < 0):
            return False
        discriminant **= 0.5
        t1 : Final[float] = (-b - discriminant) / (2 * a)
        t2 : Final[float] = (-b + discriminant) / (2 * a)
        return 0 <= t1 <= 1 or 0 <= t2 <= 1

    @property
    def x (self) -> float: return self.__cx - self.r
    @property
    def y (self) -> float: return self.__cy - self.r
    @property
    def cx (self) -> float: return self.__cx
    @property
    def cy (self) -> float: return self.__cy
    def contains(self, point : Point) -> bool:
        return (point[0] - self.cx) ** 2 + (point[1] - self.cy) ** 2 < self.r ** 2


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

    def contains(self, point : Point) -> bool:
        return (self.__x <= point[0] <= self.__x + self.w and
                self.__y <= point[1] <= self.__y + self.h)

    def collideRect (self, other : Self) -> bool:
        return (self.x <= other.x + other.w and self.x + self.w >= other.x
                and self.y <= other.y + other.h and self.y + self.h >= other.y)

    def collideSegment (self, item : SegmentHitbox) -> bool:
        sides = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        if (self.contains((item.x0, item.y0)) or
            self.contains((item.x1, item.y1))):
            return True
        def point (pos):
            return (self.x + self.w * pos[0], self.y + self.h * pos[1])
        for i in range(4):
            if item.intersects(point(sides[i]), point(sides[i+1])):
                return True
        return False

    def collideCircle (self, item : CircleHitbox) -> bool:
        # https://stackoverflow.com/questions/401847/circle-rectangle-collision-detection-intersection
        sides = [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        def point (pos):
            return (self.x + self.w * pos[0], self.y + self.h * pos[1])
        if (self.x <= item.cx <= self.x + self.w and
            self.y <= item.cy <= self.y + self.h):
            return True
        for i in range(4):
            if item.collideSegment(SegmentHitbox(*point(sides[i]),
                                                 *point(sides[i+1]))):
                return True
        return False

class AABBHitbox (Hitbox):
    def __init__ (self, x : int, y : int, *args : List[Hitbox]):
        self.__items : List[Hitbox] = []
        self.__x : float = x
        self.__y : float = y
        mx = 0
        my = 0
        for arg in args:
            mx = min(mx, args.x)
            my = min(my, args.y)
        for arg in args:
            arg.move(-mx, -my)
            self.__items.append(arg)
        self.__items.sort(key = lambda arg : (arg.y, arg.x))

    @property
    def items (self) -> List[Hitbox]:
        return self.__items

    def accept (self, visitor : HitboxVisitor) -> object:
        return visitor.acceptAABBHitbox(self)

    def collide (self, hitbox : Hitbox) -> bool:
        # TODO: Binary search
        for x in self.__items:
            if x.collide(hitbox):
                return True
        return False

    @property
    def x (self) -> float:
        return self.__x

    @property
    def y (self) -> float:
        return self.__y

    @property
    def move (self, dx : float, dy : float) -> NoReturn:
        self.__x += dx
        self.__y += dy
        for item in self.__items:
            item.move(dx, dy)

# Visitors

class HitboxVisitor (metaclass = ABCMeta):
    @abstractmethod
    def acceptRectHitbox (self, item : RectHitbox) -> NoReturn:
        raise NotImplementedError
    @abstractmethod
    def acceptCircleHitbox (self, item : CircleHitbox) -> NoReturn:
        raise NotImplementedError
    @abstractmethod
    def acceptAABBHitbox (self, item : AABBHitbox) -> NoReturn:
        raise NotImplementedError
    @abstractmethod
    def acceptSegmentHitbox (self, item : SegmentHitbox) -> NoReturn:
        raise NotImplementedError

class _RectHitboxCollideVisitor (HitboxVisitor):
    def __init__ (self, hitbox : RectHitbox):
        self.__hitbox : Final[RectHitbox] = hitbox
    def acceptRectHitbox (self, item : RectHitbox) -> bool:
        return self.__hitbox.collideRect(item)
    def acceptCircleHitbox (self, item : CircleHitbox) -> bool:
        return self.__hitbox.collideCircle(item)
    def acceptSegmentHitbox (self, item : SegmentHitbox) -> NoReturn:
        return self.__hitbox.collideSegment(item)
    def acceptAABBHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)

class _CircleHitboxCollideVisitor (HitboxVisitor):
    def __init__ (self, hitbox : CircleHitbox):
        self.__hitbox : Final[CircleHitbox] = hitbox
    def acceptRectHitbox (self, item : RectHitbox) -> bool:
        return item.collideCircle(self.__hitbox)
    def acceptCircleHitbox (self, item : CircleHitbox) -> bool:
        return self.__hitbox.collideCircle(item)
    def acceptSegmentHitbox (self, item : SegmentHitbox) -> NoReturn:
        return self.__hitbox.collideSegment(item)
    def acceptAABBHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)

class _SegmentHitboxCollideVisitor (HitboxVisitor):
    def __init__ (self, hitbox : SegmentHitbox):
        self.__hitbox : Final[SegmentHitbox] = hitbox
    def acceptRectHitbox (self, item : RectHitbox) -> bool:
        return item.collideSegment(self.__hitbox)
    def acceptCircleHitbox (self, item : CircleHitbox) -> bool:
        return item.collideSegment(self.__hitbox)
    def acceptSegmentHitbox (self, item : SegmentHitbox) -> NoReturn:
        return self.__hitbox.intersects((item.x0, item.y0), (item.x1, item.y1))
    def acceptAABBHitbox (self, item : AABBHitbox) -> bool:
        return item.collide(self.__hitbox)
