import pygame
import sys, os
root = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.append(os.path.join(root, "lib"))
import hitbox
from pygame_controller import PygameController

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
    def acceptComplexHitbox (self, item : hitbox.ComplexHitbox):
        pass
    def acceptAABBHitbox (self, item : hitbox.AABBHitbox):
        pass

def drawHitbox (item : hitbox.Hitbox, surface : pygame.Surface, colour : pygame.Color):
    visitor = DrawHitboxVisitor(surface, colour)
    item.accept(visitor)

class Game:
    def __init__ (self, fps = 30):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.fps = fps
        pygame.display.set_caption("Pygame Example -- Collisions")
        self.controller : Final[PygameController] = PygameController()
        self.main = hitbox.RectHitbox(0, 0, 50, 50)
        self.shapes = [
                hitbox.RectHitbox(300, 100, 30, 30),
                hitbox.RectHitbox(120, 30, 100, 100),
                hitbox.CircleHitbox(300, 300, 30),
                hitbox.CircleHitbox(400, 300, 15),
                hitbox.CircleHitbox(600, 300, 60),
        ]

    def run(self):
        clock = pygame.time.Clock()
        while not self.controller.shouldClose():
            self.screen.fill(pygame.Color(0, 0, 0))
            self.controller.poll()
            self.update()
            self.draw()
            ms = clock.tick()
            pygame.display.update()
            pygame.time.delay(int(1 / self.fps - ms))
        pygame.quit()

    def update (self):
        dt = 1 / self.fps
        x, y = self.controller.getJoystick()
        v = 0.25
        x *= v
        y *= v
        self.main.move(x, y)

    def draw (self):
        main_free = pygame.Color(128, 0, 0)
        main_coll = pygame.Color(255, 0, 0)
        other_free = pygame.Color(0, 128, 0)
        other_coll = pygame.Color(0, 255, 0)
        collides = False
        for shape in self.shapes:
            c = self.main.collide(shape)
            drawHitbox(shape, self.screen, other_coll if c else other_free)
            collides = collides or c
        drawHitbox(self.main, self.screen, main_coll if collides else main_free)

if __name__ == "__main__":
    game = Game()
    game.run()
