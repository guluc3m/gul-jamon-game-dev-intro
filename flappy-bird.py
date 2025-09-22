import pygame
from guljamonlib.hitbox import RectHitbox, CircleHitbox
from guljamonlib.pygame_controller import PygameController
from guljamonlib.controller import ButtonKind
from guljamonlib.clock import Clock
import random

FPS = 30
WIDTH = 800
HEIGHT = 600
GRAVITY = HEIGHT
JUMP_V = -HEIGHT // 2
MAX_V = HEIGHT * 2
PIPE_SPEED = -WIDTH // 4
PIPE_MIN_RATE = FPS // 2
PIPE_MAX_RATE = FPS
PIPE_WIDTH = 50

class Vector:
   def __init__ (self, x, y):
      self.x = x
      self.y = y

   def asTuple (self):
      return (self.x, self.y)


class Birb:
   def __init__ (self, pos, radius):
      self.hitbox = CircleHitbox(*pos.asTuple(), radius)
      self.v = 0

   def draw (self, screen):
      pygame.draw.circle(screen, pygame.Color(200, 200, 20),
                         (self.hitbox.cx, self.hitbox.cy), self.hitbox.r)

   def update (self, dt, controller):
      if controller.isShortPressed(ButtonKind.A):
         self.v = JUMP_V
      dy = self.v * dt
      dy = self.hitbox.y if dy + self.hitbox.y < 0 else dy
      self.v = min(MAX_V, self.v + GRAVITY * dt)
      self.hitbox.move(0, dy)

      return self.hitbox.y < HEIGHT

class Pipe:
   def __init__ (self, pos, size):
      self.hitbox = RectHitbox(*pos.asTuple(), *size.asTuple())

   def draw (self, screen):
      pygame.draw.rect(screen, pygame.Color(0, 200, 100),
                       pygame.Rect((self.hitbox.x, self.hitbox.y),
                                   (self.hitbox.w, self.hitbox.h)))

   def update (self, dt):
      self.hitbox.move(PIPE_SPEED* dt, 0)
      return self.hitbox.x + self.hitbox.w > 0

class Game:
   def __init__ (self):
      pygame.init()
      self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
      self.controller = PygameController()
      self.pipes = []
      self.next_pipe = 0
      r = 10
      self.birb = Birb(Vector(WIDTH // 10, (HEIGHT - r) // 2), r)

   def run (self):
      clock = Clock(FPS)
      self.lose = False
      while not self.controller.shouldClose() and not self.lose:
         self.controller.poll()
         self.nextPipe()
         self.update()
         self.draw()
         clock.delay()
      pygame.quit()

   def nextPipe (self):
      if self.next_pipe == 0:
         self.next_pipe = random.randint(PIPE_MIN_RATE, PIPE_MAX_RATE)
         space = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
         h_up = random.randint(0, space)
         h_down = HEIGHT - h_up - space
         self.pipes.append(Pipe(Vector(WIDTH, 0), Vector(PIPE_WIDTH, h_up)))
         self.pipes.append(Pipe(Vector(WIDTH, h_up + space),
                                Vector(PIPE_WIDTH, h_down)))
      self.next_pipe -= 1

   def draw (self):
      self.screen.fill(pygame.Color(0, 0, 0))
      for pipe in self.pipes:
         pipe.draw(self.screen)
      self.birb.draw(self.screen)
      pygame.display.update()

   def update (self):
      dt = 1 / FPS
      if not self.birb.update(dt, self.controller):
         self.lose = True
      for i in range(len(self.pipes) - 1, -1, -1):
         if not self.pipes[i].update(dt):
            del self.pipes[i]
         elif self.pipes[i].hitbox.collide(self.birb.hitbox):
            self.lose = True

if __name__ == "__main__":
   game = Game()
   game.run()
