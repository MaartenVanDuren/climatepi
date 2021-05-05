import RPi.GPIO as GPIO
from enum import IntEnum, unique


@unique
class RelayMode(IntEnum):
    OFF = 0
    ONE = 1
    TWO = 2
    THREE = 3


class RelayController:

    def __init__(self):
        # Set current GPIO mode.
        GPIO.setmode(GPIO.BCM)
        # Removing the warings.
        # GPIO.setwarnings(False)
        # Create a list with the GPIO numbers that we use.
        self._pin_power = 27
        self._pin_mode1 = 22
        self._pin_mode2 = 23
        self._pin_mode3 = 24
        self._pins = [self._pin_power, self._pin_mode1, self._pin_mode2, self._pin_mode3]

        # Set the mode for all pins so all will be switched.
        GPIO.setup(self._pins, GPIO.OUT, initial=GPIO.HIGH)

        # HIGH = relay at default position.
        # LOW = relay switched to other position.

        self._mode = None
        self.mode_1()

    def mode_off(self):
        # Switch modes 1, 2, 3 to default, and switch power off.
        GPIO.output(self._pin_mode3, GPIO.HIGH)
        GPIO.output(self._pin_mode2, GPIO.HIGH)
        GPIO.output(self._pin_mode1, GPIO.HIGH)
        GPIO.output(self._pin_power, GPIO.LOW)
        self._mode = RelayMode.OFF

    def mode_1(self):
        # Switch modes 2, 3, and power to default, and mode 1 on.
        GPIO.output(self._pin_mode3, GPIO.HIGH)
        GPIO.output(self._pin_mode2, GPIO.HIGH)
        # Only switch power on if both mode 2 and 3 are off.
        assert(GPIO.input(self._pin_mode3) == GPIO.HIGH & GPIO.input(self._pin_mode2) == GPIO.HIGH)
        GPIO.output(self._pin_mode1, GPIO.LOW)
        GPIO.output(self._pin_power, GPIO.HIGH)
        self._mode = RelayMode.ONE

    def mode_2(self):
        # Switch modes 3, and power to default, and switch mode 1, and 2 on.
        GPIO.output(self._pin_mode3, GPIO.HIGH)
        # Only switch power to mode 2 on if mode 3 is off.
        assert (GPIO.input(self._pin_mode3) == GPIO.HIGH)
        GPIO.output(self._pin_mode1, GPIO.LOW)
        GPIO.output(self._pin_power, GPIO.HIGH)
        GPIO.output(self._pin_mode2, GPIO.LOW)
        self._mode = RelayMode.TWO

    def mode_3(self):
        # Switch modes 2, and power to default, and switch modes 1, and 3 on.
        GPIO.output(self._pin_mode2, GPIO.HIGH)
        # Only switch power to mode 3 on if mode 2 is off.
        assert (GPIO.input(self._pin_mode2) == GPIO.HIGH)
        GPIO.output(self._pin_mode1, GPIO.LOW)
        GPIO.output(self._pin_power, GPIO.HIGH)
        GPIO.output(self._pin_mode3, GPIO.LOW)
        self._mode = RelayMode.THREE

    @property
    def mode(self):
        return self._mode

    def close(self):
        GPIO.cleanup()

    def __del__(self):
        self.close()
