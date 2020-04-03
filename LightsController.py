from lifxlan import LifxLAN
import config
import math

class LightsController:
    WARM_WHITE = [58275, 0, 65535, 3000]
    MAX_VALUE = 65535
    SCALE = [MAX_VALUE / 360, MAX_VALUE / 100, MAX_VALUE / 100, 1]

    ROTATE_CHANGE_COLOR_DELTA = 1 * config.ChangeColorSpeed['value']
    DIM_DELTA = 5.0

    def __init__(self, number_of_devices=1):
        self.device_controller = LifxLAN(number_of_devices)
        self.colour = None
        self.power = None
        self.reset_color()
        self.turn_on()
        if config.PrintLog:
            print "Light switched on with warm white"

    def reset_color(self):
        self.colour = [49, 0, 50.0, 3000]
        self.set_colour()

    def put_colour_in_loop(self):
        if self.colour[1] == 0:
            self.colour[1] = 80

    def take_colour_out_of_loop(self):
        self.colour[1] = 0

    def roll_forward(self):
        if not self.power:
            return
        self.put_colour_in_loop()
        self.colour[0] = (self.colour[0] + self.ROTATE_CHANGE_COLOR_DELTA) % 360
        self.set_colour()

    def roll_backward(self):
        if not self.power:
            return
        self.put_colour_in_loop()
        self.colour[0] = (self.colour[0] - self.ROTATE_CHANGE_COLOR_DELTA) % 360
        self.set_colour()

    def location_on_circle(self, x, y):
        degrees = math.degrees(math.atan(y/x))
        if x > 0 and y < 0:
            degrees += 180
        elif x > 0 and y > 0:
            degrees += 180
        elif x < 0 and y > 0:
            degrees += 360
        length = min(100, math.sqrt(x*x + y*y))
        self.colour[0] = degrees
        self.colour[1] = length
        self.set_colour()

    def increase_brightness(self):
        self.colour[2] = min(100.0, self.colour[2] + self.DIM_DELTA)
        self.set_colour()

    def decrease_brightness(self):
        self.colour[2] = max(0.2, self.colour[2] - self.DIM_DELTA)
        self.set_colour()

    def switch_power(self):
        self.power = not self.power
        if self.power:
            self.reset_color()
        self.set_power()

    def turn_off(self):
        if not self.power:
            return
        self.power = False
        self.set_power()

    def turn_on(self):
        if self.power:
            return
        self.power = True
        self.reset_color()
        self.set_power()

    def set_colour(self):
        if config.PrintLog:
            print "Setting colours: ", [self.SCALE[i] * self.colour[i] for i in range(4)]
        self.device_controller.set_color_all_lights([self.SCALE[i] * self.colour[i] for i in range(4)])

    def set_power(self):
        self.device_controller.set_power_all_lights(self.power)
