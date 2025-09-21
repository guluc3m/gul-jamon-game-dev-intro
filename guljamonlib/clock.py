import time

class Clock:
    def __init__ (self, fps : int):
        self.__last = time.time()
        self.__spf = 1 / fps

    def delay (self):
        new = time.time()
        dt = new - self.__last
        time.sleep(max(0, self.__spf - dt))
        self.__last = time.time()
