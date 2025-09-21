"""
3V3 power           (1)     (2)             5V power
GPIO 2 (SDA)        (3)     (4)             5V power
GPIO 3 (SCL)        (5)     (6)             Ground
GPIO 4 (GPCLK0)     (7)     (8)             GPIO 14 (TXD)
Ground              (9)     (10)            GPIO 15 (RXD)
GPIO 17             (11)    (12)            GPIO 18 (PCM_CLK)
GPIO 27             (13)    (14)            Ground
GPIO 22             (15)    (16)            GPIO 23
3V3 power           (17)    (18)            GPIO 24
GPIO 10 (MOSI)      (19)    (20)            Ground
GPIO 9 (MISO)       (21)    (22)            GPIO 25
GPIO 11 (SCLK)      (23)    (24)            GPIO 8 (CE0)
Ground              (25)    (26)            GPIO 7 (CE1)
GPIO 0 (ID_SD)      (27)    (28)            GPIO 1 (ID_SC)
GPIO 5              (29)    (30)            Ground
GPIO 6              (31)    (32)            GPIO 12 (PWM0)
GPIO 13 (PWM1)      (33)    (34)            Ground
GPIO 19 (PCM_FS)    (35)    (36)            GPIO 16
GPIO 26             (37)    (38)            GPIO 20 (PCM_DIN)
Ground              (39)    (40)            GPIO 21 (PCM_DOUT)
"""

from RPi import GPIO

BUTTON_A = 16       # GPIO 23
BUTTON_B = 18       # GPIO 24

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
if GPIO.input(16) == GPIO.HIGH:
    print("Ok")

GPIO.cleanup()
