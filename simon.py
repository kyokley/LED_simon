import pigpio
import time
import random

GREEN_PIN = 17
RED_PIN = 27
BLUE_PIN = 22

GREEN_BUTTON_PIN = 24
RED_BUTTON_PIN = 25
BLUE_BUTTON_PIN = 12

pi = pigpio.pi()

class Led(object):
    def __init__(self, pin):
        self.pin = pin
        self._pi = pi
        self._pi.set_mode(self.pin, pigpio.OUTPUT)

    def on(self):
        self._pi.write(self.pin, 1)

    def off(self):
        self._pi.write(self.pin, 0)

class Button(object):
    def __init__(self, pin):
        self.pin = pin
        self._pi = pi
        self._pi.set_mode(self.pin, pigpio.INPUT)
        self._pi.set_pull_up_down(self.pin, pigpio.PUD_UP)

    def status(self):
        return not bool(self._pi.read(self.pin))

def test_leds():
    green_led = Led(GREEN_PIN)
    red_led = Led(RED_PIN)
    blue_led = Led(BLUE_PIN)

    ALL_LEDS = (green_led, red_led, blue_led)
    try:
        while True:
            for led in ALL_LEDS:
                func = random.choice([led.on, led.off])
                func()
                time.sleep(.1)
    except KeyboardInterrupt:
        for led in ALL_LEDS:
            led.off()

class Game(object):
    def __init__(self, leds, buttons):
        self.seq = []
        self.leds = leds
        self.buttons = buttons
        self.led_dict = dict(zip(leds, buttons))
        self.button_dict = dict(zip(buttons, leds))
        self.done = False

    def run(self):
        while not self.done:
            self.generate()
            self.check_input()
            time.sleep(.5)

    def generate(self):
        self.seq.append(random.choice(self.leds))

        for led in self.seq:
            led.on()
            time.sleep(1)
            led.off()

    def get_inputs(self):
        while True:
            for button in self.buttons:
                if button.status():
                    self.button_dict[button].on()
                    yield button
                    self.button_dict[button].off()
            time.sleep(.1)

    def game_over(self):
        for i in xrange(5):
            for led in self.leds:
                led.on()

            time.sleep(.25)

            for led in self.leds:
                led.off()

        self.done = True

    def check_input(self):
        inputs = self.get_inputs()

        for led in self.seq:
            pressed = next(inputs)
            if led != self.button_dict[pressed]:
                self.game_over()
                break

def main():
    green_led = Led(GREEN_PIN)
    red_led = Led(RED_PIN)
    blue_led = Led(BLUE_PIN)

    ALL_LEDS = (green_led, red_led, blue_led)

    green_button = Button(GREEN_BUTTON_PIN)
    red_button = Button(RED_BUTTON_PIN)
    blue_button = Button(BLUE_BUTTON_PIN)

    ALL_BUTTONS = (green_button,
                   red_button,
                   blue_button)

    game = Game(ALL_LEDS, ALL_BUTTONS)
    game.run()

if __name__ == '__main__':
    main()
