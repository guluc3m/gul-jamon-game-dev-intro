from typing import Final, Dict, List
import pygame.locals

from guljamonlib.controller import ControllerInterface, ButtonKind, Controller

type PygameKeyType = int
type PygameKeyMap = Dict[ButtonKind, List[PygameKeyType]]
default_keymap : PygameKeyMap = {
    ButtonKind.Quit   : [pygame.locals.K_q],
    ButtonKind.Up     : [pygame.locals.K_w, pygame.locals.K_UP],
    ButtonKind.Down   : [pygame.locals.K_s, pygame.locals.K_DOWN],
    ButtonKind.Left   : [pygame.locals.K_a, pygame.locals.K_LEFT],
    ButtonKind.Right  : [pygame.locals.K_d, pygame.locals.K_RIGHT],
    ButtonKind.Start  : [pygame.locals.K_RETURN],
    ButtonKind.Select : [pygame.locals.K_BACKSPACE],
    ButtonKind.A      : [pygame.locals.K_SPACE],
    ButtonKind.B      : [pygame.locals.K_z],
    ButtonKind.X      : [pygame.locals.K_x],
    ButtonKind.Y      : [pygame.locals.K_c]
}

class PygameControllerInterface (ControllerInterface):
    def __init__ (self, keymap : PygameKeyMap):
        self.__keymap : Final[PygameKeyMap] = keymap
        self.__revmap : Final[Dict[PygameKeyType, ButtonKind]] = {
            key : button for (button, keys) in self.__keymap.items()
                         for key in keys}
        self.__state  : list[int] = PygameControllerInterface.emptyState()
        self.__close  : bool = False

    def poll (self) -> list[int]:
        self.__close = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__close = True
            elif event.type == pygame.KEYDOWN:
                if event.key in self.__revmap:
                    self.__state[self.__revmap[event.key].value] = 1
            elif event.type == pygame.KEYUP:
                if event.key in self.__revmap:
                    self.__state[self.__revmap[event.key].value] = 0
        return [x for x in self.__state]

    def shouldClose (self) -> bool:
        return self.__close

    def getJoystick (self) -> tuple[float, float]:
        return (0, 0)

def PygameController (keymap : PygameKeyMap = default_keymap, long : int = 2):
    return Controller(PygameControllerInterface(default_keymap), long)
