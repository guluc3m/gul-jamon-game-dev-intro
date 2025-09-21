import pygame
import sys, os
#root = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
#sys.path.append(os.path.join(root, "lib")) -> Omitible tras instalar el proyecto
import hitbox
from controller import ButtonKind
from pygame_controller import PygameController
import math
from clock import Clock

BEAMS_PER_SEC = 10
BEAM_LENGTH = 4
MAX_ENEMY_BEAM_SPEED = 100  # px/second
PLAYER_BEAM_SPEED = 500     # px/second
PLAYER_SPEED = 200          # px/second
ENEMY_MAX_HEALTH = 100
PLAYER_COOLDOWN = 1

class DrawHitboxVisitor (hitbox.HitboxVisitor):
    def __init__ (self, surface : pygame.Surface, colour : pygame.Color):
        self.__colour = colour
        self.__surface = surface
    def acceptRectHitbox (self, item : hitbox.RectHitbox):
        pygame.draw.rect(self.__surface, self.__colour,
                         pygame.Rect((item.x, item.y), (item.w, item.h)))
    def acceptCircleHitbox (self, item : hitbox.CircleHitbox):
        pygame.draw.circle(self.__surface, self.__colour,
                          (item.cx, item.cy), item.r)
    def acceptAABBHitbox (self, item : hitbox.AABBHitbox):
        pass
    def acceptSegmentHitbox (self, item : hitbox.SegmentHitbox):
        pygame.draw.line(self.__surface, self.__colour,
                         (item.x0, item.y0), (item.x1, item.y1),
                         width = 2)

class Beam:
    def __init__ (self,
                  hitbox : hitbox.Hitbox,
                  colour : pygame.Color,
                  screen : tuple[int, int],
                  speed  : tuple[float, float]):
        self.__colour = colour
        self.__hitbox = hitbox
        self.__speed = speed
        self.__screen = screen

    @property
    def hitbox (self) -> hitbox.Hitbox:
        return self.__hitbox

    def draw (self, surface : pygame.Surface):
        visitor = DrawHitboxVisitor(surface, self.__colour)
        self.__hitbox.accept(visitor)

    def update (self, dt : float) -> bool:
        extra = 20
        self.__hitbox.move(self.__speed[0] * dt, self.__speed[1] * dt)
        return ((0 <= self.hitbox.x <= self.__screen[0]
                    or 0 <= self.hitbox.x + extra <= self.__screen[0])
            and ((0 <= self.hitbox.y <= self.__screen[1]
                    or 0 <= self.hitbox.y + extra <= self.__screen[1])))

class Player:
    def __init__ (self,
                  x      : int,
                  y      : int,
                  screen : tuple[int, int],
                  size   : int = 10):
        self.__hitbox = hitbox.CircleHitbox(x + size // 2, y + size // 2, size)
        self.__colour = pygame.Color(255, 0, 0)
        self.__screen = screen
        self.__elapsed = 0
        self.__health = 3
        self.__cooldown = 0

    @property
    def health (self) -> int : return self.__health
    @property
    def hitbox (self) -> hitbox.Hitbox: return self.__hitbox

    def draw (self, surface : pygame.Surface):
        if self.__cooldown > 0:
            pygame.draw.circle(surface, pygame.Color(0, 255, 100),
                               (self.__hitbox.cx, self.__hitbox.cy),
                               self.__hitbox.r+2)
        pygame.draw.circle(surface, self.__colour,
                           (self.__hitbox.cx, self.__hitbox.cy),
                           self.__hitbox.r)
        for i in range(self.__health):
            pygame.draw.rect(surface, self.__colour,
                             pygame.Rect((50+20*i, 500), (15, 10)))


    def move (self, x : float, y : float, dt : float):
        self.__hitbox.move(x * PLAYER_SPEED * dt, y * PLAYER_SPEED * dt)
        if self.__cooldown > 0:
            self.__cooldown = 0 if self.__cooldown - dt <= 0 else self.__cooldown - dt


    def getBeams (self, dt : float) -> list[Beam]:
        beams = []
        self.__elapsed += dt
        if self.__elapsed >= 1 / BEAMS_PER_SEC:
            self.__elapsed = 0
            x = self.hitbox.x + self.hitbox.r // 2
            y = self.hitbox.y
            box = hitbox.SegmentHitbox(x, y, x, y - BEAM_LENGTH)
            colour = pygame.Color(255, 128, 0)
            speed  = (0, -PLAYER_BEAM_SPEED)
            beams.append(Beam(box, colour, self.__screen, speed))
        return beams

    def damage (self):
        if self.__cooldown == 0:
            self.__health -= 1
            self.__cooldown = PLAYER_COOLDOWN

class Pattern:
    def __init__ (self,
                  shape  : str,
                  count  : int,
                  colour : tuple[int, int, int],
                  speed  : float):
        self.shape = shape
        self.count = count
        self.colour = pygame.Color(*colour)
        self.speed = speed

class Action:
    def __init__ (self, *,
                  time    : float,
                  action  : str,
                  rate    : float,
                  rel_pos : tuple[float, float],
                  pattern : Pattern):
        self.time = time
        self.action = action
        self.rate = rate
        self.rel_pos = rel_pos
        self.pattern = pattern

class Enemy:
    def __init__ (self, x : int, y : int, w : int, h : int, screen):
        self.__colour  = pygame.Color(0, 0, 255)
        self.__hitbox  = hitbox.RectHitbox(x - w // 2, y - h // 2, w, h)
        self.__screen  = screen
        self.__elapsed = 0
        self.__shoot_elapsed = 0
        self.__health = ENEMY_MAX_HEALTH
        self.__state = 0
        self.__script = [
            Action(time    = 3,
                   action  = "stay",
                   rate    = 1.0,
                   rel_pos = (0.5, 0.1),
                   pattern = Pattern("circle", 40, (0, 255, 0), 1.0)),
            Action(time    = 2,
                   action  = "move",
                   rate    = 1.0,
                   rel_pos = (0.1, 0.2),
                   pattern = Pattern("circle", 20, (0, 255, 0), 0.5)),
            Action(time    = 3,
                   action  = "stay",
                   rate    = 1.0,
                   rel_pos = (0.1, 0.2),
                   pattern = Pattern("circle", 40, (0, 255, 0), 1.0)),
            Action(time    = 5,
                   action  = "move",
                   rate    = 1.0,
                   rel_pos = (0.9, 0.05),
                   pattern = Pattern("circle", 20, (0, 255, 0), 0.5)),
            Action(time    = 5,
                   action  = "move",
                   rate    = 1.0,
                   rel_pos = (0.5, 0.1),
                   pattern = Pattern("circle", 40, (0, 255, 0), 1.0)),
        ]

    @property
    def health (self) -> int : return self.__health
    @property
    def hitbox (self) -> hitbox.Hitbox: return self.__hitbox

    def draw (self, surface : pygame.Surface):
        pygame.draw.rect(surface, self.__colour,
                         pygame.Rect((self.__hitbox.x, self.__hitbox.y),
                                     (self.__hitbox.w, self.__hitbox.h)))
        for i in range(self.__health):
            pygame.draw.rect(surface, self.__colour,
                             pygame.Rect((200+i*4, 550), (4, 20)))

    def __circlePattern (self,
                         hitbox_maker,
                         speed  : int,
                         count  : int,
                         colour : pygame.Color) -> list[Beam]:
        # r² = (x - cx)² + (y - cy)²
        # r² = x'² + y'² => y = sqrt(r² - x²)
        beams = []
        cx = self.hitbox.x + self.hitbox.w // 2
        cy = self.hitbox.y + self.hitbox.h // 2
        for i in range(count // 2 + 2):
            x = 2 * (i / (count // 2 + 1) - 0.5)
            y = math.sqrt(1 - x ** 2)
            hitbox = hitbox_maker(x + cx, y + cy)
            beams.append(Beam(hitbox, colour, self.__screen,
                              (x * speed, y * speed)))
            hitbox = hitbox_maker(x + cx, -y + cy)
            beams.append(Beam(hitbox, colour, self.__screen,
                              (x * speed, -y * speed)))
        return beams

    def __circleCirclePattern (self,
                               radius : int,
                               speed  : int,
                               count  : int,
                               colour : pygame.Color) -> list[Beam]:
        maker = lambda x, y : hitbox.CircleHitbox(x, y, radius)
        return self.__circlePattern(maker, speed, count, colour)

    def update (self, dt : float) -> list[Beam]:
        beams = []
        self.__elapsed += dt
        self.__shoot_elapsed += dt
        script = self.__script[self.__state]
        if self.__shoot_elapsed >= script.rate:
            self.__shoot_elapsed = 0
            speed = script.pattern.speed * MAX_ENEMY_BEAM_SPEED
            colour = script.pattern.colour
            count = script.pattern.count
            if script.pattern.shape == "circle":
                beams = self.__circleCirclePattern(4, speed, count, colour)
        if script.action == "move":
            x, y = script.rel_pos
            x *= self.__screen[0]
            y *= self.__screen[1]
            dx = x - self.__hitbox.x
            dy = y - self.__hitbox.y
            tm = script.time - self.__elapsed
            if tm != 0:
                sx = dx / tm
                sy = dy / tm
                self.__hitbox.move(sx * dt, sy * dt)
        if self.__elapsed >= script.time:
            self.__elapsed = 0
            self.__shoot_elapsed = 0
            self.__state += 1
            self.__state %= len(self.__script)
            x = script.rel_pos[0] * self.__screen[0]
            y = script.rel_pos[1] * self.__screen[1]
            self.__hitbox.move(x - self.__hitbox.x, y - self.__hitbox.y)
        return beams

    def damage (self):
        self.__health -= 1

class Game:
    def __init__ (self, width : int, height : int, fps = 30):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.fps = fps
        pygame.display.set_caption("Pygame Example -- Bullet Hell")
        self.controller : Final[PygameController] = PygameController()
        self.player = Player(x      = width // 2,
                             y      = height * 8 // 10,
                             screen = (width, height),
                             size   = 4)
        self.enemy = Enemy(width // 2, height * 2 // 10, 20, 40, (width, height))
        self.pbeams = []
        self.ebeams = []

    def run (self):
        clock = Clock(self.fps)
        while not self.controller.shouldClose():
            self.controller.poll()
            self.update()
            self.screen.fill(pygame.Color(0, 0, 0))
            self.draw()
            pygame.display.update()
            clock.delay()
        pygame.quit()

    def update (self):
        if self.player.health < 0 or self.enemy.health < 0:
            pygame.quit()
        dt = 1 / self.fps
        self.player.move(*self.controller.getJoystick(), dt)
        self.ebeams += self.enemy.update(dt)
        self.pbeams += self.player.getBeams(dt)
        for i in range(len(self.pbeams) - 1, -1, -1):
            if not self.pbeams[i].update(dt):
                del self.pbeams[i]
            elif self.enemy.hitbox.collide(self.pbeams[i].hitbox):
                self.enemy.damage()
                del self.pbeams[i]
        for i in range(len(self.ebeams) - 1, -1, -1):
            if not self.ebeams[i].update(dt):
                del self.ebeams[i]
            elif self.player.hitbox.collide(self.ebeams[i].hitbox):
                self.player.damage()
                del self.ebeams[i]

    def draw (self):
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        for beam in self.pbeams:
            beam.draw(self.screen)
        for beam in self.ebeams:
            beam.draw(self.screen)

if __name__ == "__main__":
    game = Game(800, 600, fps = 400)
    game.run()
