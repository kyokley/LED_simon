import pigpio
import time
import random

GREEN_PIN = 17
RED_PIN = 27
BLUE_PIN = 22

GREEN_BUTTON_PIN = 24
RED_BUTTON_PIN = 25
BLUE_BUTTON_PIN = 12

BUZZER_PIN = 18
DUTY_CYCLE = 8000

FREQ0 = 800
FREQ1 = 1200
FREQ2 = 1600
FREQ3 = 2000

pi = pigpio.pi()

pi.set_mode(BUZZER_PIN, pigpio.OUTPUT)
class Buzzer(object):

    @staticmethod
    def stop():
        pi.hardware_PWM(BUZZER_PIN, 0, 0)

    @staticmethod
    def play0():
        pi.hardware_PWM(BUZZER_PIN, FREQ0, DUTY_CYCLE * 1.5)

    @staticmethod
    def play1():
        pi.hardware_PWM(BUZZER_PIN, FREQ1, DUTY_CYCLE)

    @staticmethod
    def play2():
        pi.hardware_PWM(BUZZER_PIN, FREQ2, DUTY_CYCLE)

    @staticmethod
    def play3():
        pi.hardware_PWM(BUZZER_PIN, FREQ3, DUTY_CYCLE)


class Led(object):
    def __init__(self, pin, sound):
        self.pin = pin
        self._pi = pi
        self._pi.set_mode(self.pin, pigpio.OUTPUT)
        self.sound = sound

    def on(self):
        self._pi.write(self.pin, 1)
        self.sound()

    def off(self):
        self._pi.write(self.pin, 0)
        Buzzer.stop()

class Button(object):
    def __init__(self, pin):
        self.pin = pin
        self._pi = pi
        self._pi.set_mode(self.pin, pigpio.INPUT)
        self._pi.set_pull_up_down(self.pin, pigpio.PUD_UP)

    def status(self):
        return not bool(self._pi.read(self.pin))

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
            time.sleep(.25)

    def get_inputs(self):
        while True:
            for button in self.buttons:
                if button.status():
                    self.button_dict[button].on()
                    while button.status():
                        time.sleep(.1)
                    self.button_dict[button].off()
                    yield button
            time.sleep(.1)

    def game_over(self):
        for i in xrange(5):
            for led in self.leds:
                led.on()
            Buzzer.play0()

            time.sleep(.25)

            for led in self.leds:
                led.off()

            time.sleep(.25)

        self.done = True
        time.sleep(1)

    def check_input(self):
        inputs = self.get_inputs()

        for led in self.seq:
            pressed = next(inputs)
            if led != self.button_dict[pressed]:
                self.game_over()
                break

def main():
    green_led = Led(GREEN_PIN, Buzzer.play1)
    red_led = Led(RED_PIN, Buzzer.play2)
    blue_led = Led(BLUE_PIN, Buzzer.play3)

    ALL_LEDS = (green_led, red_led, blue_led)

    green_button = Button(GREEN_BUTTON_PIN)
    red_button = Button(RED_BUTTON_PIN)
    blue_button = Button(BLUE_BUTTON_PIN)

    ALL_BUTTONS = (green_button,
                   red_button,
                   blue_button)

    while True:
        game = Game(ALL_LEDS, ALL_BUTTONS)
        game.run()

if __name__ == '__main__':
    main()
