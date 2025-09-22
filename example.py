import pygame
import pygame.locals
import time
from guljamonlib.pygame_controller import PygameController
from guljamonlib.controller import ButtonKind
from guljamonlib.clock import Clock
from guljamonlib.hitbox import RectHitbox

STEPS = 160

class Entity:
    def __init__ (self, x, y, w, h, colour):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.colour = colour

    def draw (self, screen):
        pygame.draw.rect(screen, self.colour,
                         pygame.Rect((self.x, self.y), (self.w, self.h)))

class Player (Entity):
    def __init__ (self, x, y):
        super().__init__(x, y, 60, 40, pygame.Color(255, 255, 0))
        self.v = 200
        self.hitbox = RectHitbox(self.x, self.y, self.w, self.h)

    def move_x (self, dt):
        self.x = self.x + self.v * dt

    def move_y (self, dt):
        self.y = self.y + self.v * dt

    def update (self, dt, controller, walls):
        dx, dy = controller.getJoystick();
        old_y = self.y

        # Move in x-axis
        collides = False
        for step in range(STEPS):
            old_x = self.x
            self.move_x(dt * dx / STEPS)
            self.hitbox.move(self.x - self.hitbox.x, 0)
            for wall in walls:
                if wall.hitbox.collide(self.hitbox):
                    collides = True
                    break
            if collides:
                self.x = old_x
                self.hitbox.move(self.x - self.hitbox.x, 0)
                break

        # Move in y-axis
        collides = False
        for step in range(STEPS):
            old_y = self.y
            self.move_y(dt * dy / STEPS)
            self.hitbox.move(0, self.y - self.hitbox.y)
            for wall in walls:
                if wall.hitbox.collide(self.hitbox):
                    collides = True
                    break
            if collides:
                self.y = old_y
                self.hitbox.move(0, self.y - self.hitbox.y)
                break

class Enemy (Entity):
    def __init__ (self, x, y):
        super().__init__(x, y, 60, 40, pygame.Color(255, 18, 42))
        self.hitbox = RectHitbox(self.x, self.y, self.w, self.h)

    def update (self, dt, player):
        pass

class Wall (Entity):
    def __init__ (self, x, y, w, h):
        super().__init__(x, y, w, h, pygame.Color(128, 128, 12))
        self.hitbox = RectHitbox(self.x, self.y, self.w, self.h)

    def update (self, dt):
        pass

class Game:
    def __init__ (self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.background = 0
        self.player = Player(20, 300)
        self.enemy = Enemy(200, 300)
        self.fps = 30
        self.controller = PygameController()
        self.walls = [
            Wall (0, 500, 200, 40),
            Wall (400, 300, 40, 200),
        ]

    def run (self):
        self.running = True
        clock = Clock(self.fps)
        while self.running:
            self.poll()
            self.update()
            self.draw()
            clock.delay()
        pygame.quit()

    def draw (self):
        self.screen.fill(pygame.Color(self.background, 0, 0))
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        for wall in self.walls:
            wall.draw(self.screen)
        pygame.display.flip()

    def update (self):
        dt = 1 / self.fps
        self.player.update(dt, self.controller, self.walls)
        self.enemy.update(dt, self.player)
        for wall in self.walls:
            wall.draw(self.screen)
        self.background = (self.background + 1) % 256

    def poll (self):
        self.controller.poll()
        self.running = not self.controller.shouldClose()

game = Game()
game.run()
