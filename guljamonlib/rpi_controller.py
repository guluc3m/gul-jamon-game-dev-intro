import subprocess
from guljamonlib.controller import ControllerInterface, ButtonKind, Controller

class RPiControllerInterface (ControllerInterface):
   def __init__ (self, host : str):
      self.__proc = subprocess.Popen(
         ['sshpass', '-ppi', 'ssh', f'pi@{host}', 'python3', "/home/pi/program.py"],
         stdout = subprocess.PIPE,
         stdin  = subprocess.PIPE)
      self.__message = "7"
      print(self.__proc.stdout.readline().decode())

   def poll (self) -> list[int]:
      self.__proc.stdin.write(f"{self.__message}\n".encode())
      self.__proc.stdin.flush()
      button = int(self.__proc.stdout.readline().decode())
      state = RPiControllerInterface.emptyState()
      state[ButtonKind.A.value] = button
      print(button)
      return state

   def shouldClose (self) -> bool:
      return False

   def getJoystick (self) -> tuple[float, float]:
      return (0, 0)

   def setMessage (self, message):
      self.__message = message

def RPiController (host : str):
   return Controller(RPiControllerInterface(host))
