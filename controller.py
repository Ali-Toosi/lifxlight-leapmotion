from LightsController import LightsController
from LeapListener import LeapListener, Leap
import ActionHandler
import sys
import config

if __name__ == '__main__':
    lights_controller = LightsController()
    leap_listener = LeapListener(ActionHandler.ActionHandler(lights_controller))
    controller = Leap.Controller()
    controller.add_listener(leap_listener)

    change_settings = raw_input("Change default settings? (Y/N) : ")
    if change_settings.lower() in ['y', 'yes']:
        for item in config.prompts:
            value = raw_input("{}? (Y/N) - default is {}: ".format(item['verbose_name'], "Yes" if item['enabled'] else "No"))
            if value == '':
                continue
            item['enabled'] = value.lower() in ['y', 'yes']

    print "\nEnjoy! Press enter whenever you want to close the program..."

    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(leap_listener)
