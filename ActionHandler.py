import config


class ActionHandler:
    ROLL_FORWARD = "roll_forward"
    ROLL_BACKWARD = "roll_backward"
    SWITCH = "switch"
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    INC_BRIGHTNESS = "inc_bright"
    DEC_BRIGHTNESS = "dec_bright"
    RESET = "reset"
    EXACT_LOCATION = "location"

    action_mapping = {
        ROLL_FORWARD: "roll_forward",
        ROLL_BACKWARD: "roll_backward",
        SWITCH: "switch_power",
        TURN_ON: "turn_on",
        TURN_OFF: "turn_off",
        INC_BRIGHTNESS: "increase_brightness",
        DEC_BRIGHTNESS: "decrease_brightness",
        RESET: "reset_color",
        EXACT_LOCATION: "location_on_circle"
    }

    def __init__(self, lights_controller):
        self.lights_controller = lights_controller
        self.action_arguments = []

    def handle(self, action):
        if config.PrintLog:
            print "Action to handle: ", action
        if action not in self.action_mapping.keys():
            return
        method = getattr(self.lights_controller, self.action_mapping[action])
        method(*self.action_arguments if action == self.EXACT_LOCATION else [])
