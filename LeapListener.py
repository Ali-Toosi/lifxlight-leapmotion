import os, sys, inspect, thread, time
from config import LeapMotionSDKLibrary as arch_dir

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap
from Leap import CircleGesture, KeyTapGesture, SwipeGesture
import config


class LeapListener(Leap.Listener):
    state_mapping = {
        Leap.Gesture.STATE_START: "STATE_START",
        Leap.Gesture.STATE_UPDATE: "STATE_UPDATE",
        Leap.Gesture.STATE_STOP: "STATE_STOP",
        Leap.Gesture.STATE_INVALID: "STATE_INVALID"
    }
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def __init__(self, action_handler, *args, **kwargs):
        super(LeapListener, self).__init__(*args, **kwargs)
        self.action_handler = action_handler
        self.fingers_state = [None for _ in range(5)]
        self.dim_memory = {
            'last_height': None,
            'number_of_frames': 0
        }

    def on_init(self, controller):
        controller.config.set('Gesture.KeyTap.MinDownVelocity', 20)
        controller.config.save()
        if config.PrintLog:
            print "Sensor Initialized"

    def on_connect(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        if config.PrintLog:
            print "Sensor Connected"

    def set_fingers_state(self, controller):
        frame = controller.frame()
        if frame.hands.is_empty:
            self.fingers_state = [None for _ in range(5)]
            return
        hand = frame.hands.rightmost
        palm_vector = hand.palm_position
        fingers_distance = []
        for finger in hand.fingers:
            fingers_distance.append((finger.type, finger.tip_position.distance_to(palm_vector)))

        def open_distance(x):
            open_distances = [85, 89, 90, 89, 85]
            return x[1] >= open_distances[x[0]]

        def close_distance(x):
            closed_distances = [70, 70, 75, 70, 65]
            return x[1] <= closed_distances[x[0]]

        for distance in fingers_distance:
            if open_distance(distance):
                self.fingers_state[distance[0]] = 'o'
            elif close_distance(distance):
                self.fingers_state[distance[0]] = 'c'
            else:
                self.fingers_state[distance[0]] = None

    def hand_open(self):
        return all(self.fingers_state[i] == 'o' for i in range(5))

    def hand_closed(self):
        return all(self.fingers_state[i] == 'c' for i in range(5))

    def open_fingers(self):
        return [i for i in range(5) if self.fingers_state[i] == 'o']

    def closed_fingers(self):
        return [i for i in range(5) if self.fingers_state[i] == 'c']

    def detect_rotation(self, controller, gesture):
        if gesture.type == Leap.Gesture.TYPE_CIRCLE:
            circle = CircleGesture(gesture)
            if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI / 2:
                is_clockwise = True
            else:
                is_clockwise = False

            swept_angle = 0
            if circle.state != Leap.Gesture.STATE_START:
                previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                swept_angle = (circle.progress - previous_update.progress) * 2 * Leap.PI
                if circle.progress > 1.3:
                    if is_clockwise:
                        return self.action_handler.ROLL_FORWARD
                    else:
                        return self.action_handler.ROLL_BACKWARD
        return None

    def detect_tap(self, controller, gesture):
        if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
            keytap = KeyTapGesture(gesture)
            if len(gesture.hands) == 1:
                open_fingers = self.open_fingers()
                if len(open_fingers) == 1 and open_fingers[0] == 1:
                    return self.action_handler.SWITCH
        return None

    def detect_swipe(self, controller, gesture):
        if gesture.type == Leap.Gesture.TYPE_SWIPE:
            swipe = SwipeGesture(gesture)
            open_fingers = self.open_fingers()
            if not len(open_fingers) == 1 or open_fingers[0] != 1:
                return None
            if swipe.direction[0] > 0:
                return self.action_handler.TURN_ON
            else:
                return self.action_handler.TURN_OFF
        return None

    def detect_dim(self, controller):
        def reset_memory():
            self.dim_memory['number_of_frames'] = 0
            self.dim_memory['last_height'] = None

        frame = controller.frame()

        if frame.hands.is_empty:
            reset_memory()
            return None

        if not self.hand_open():
            reset_memory()
            return None

        hand = frame.hands.rightmost
        height = hand.palm_position[1]
        result = None
        if self.dim_memory['number_of_frames'] > 20 and abs(height - self.dim_memory['last_height']) > 3.5:
            if height > self.dim_memory['last_height']:
                result = self.action_handler.INC_BRIGHTNESS
            else:
                result = self.action_handler.DEC_BRIGHTNESS

        self.dim_memory['number_of_frames'] += 1
        self.dim_memory['last_height'] = height

        return result

    def detect_pinch(self, controller):
        frame = controller.frame()

        if frame.hands.is_empty:
            return None

        fingers = frame.hands.rightmost.fingers

        target_fingers_distance = fingers[0].tip_position.distance_to(fingers[1].tip_position)

        if target_fingers_distance <= 15 \
                and all(self.fingers_state[i] == 'c' for i in range(2, 5)) \
                and all(self.fingers_state[i] != 'c' for i in [0, 1]):
            return self.action_handler.RESET

        return None

    def detect_thumb_out(self, controller):
        frame = controller.frame()

        if frame.hands.is_empty:
            return None

        if self.fingers_state[0] == 'o' and all(self.fingers_state[i] == 'c' for i in range(1, 5)):
            return self.action_handler.RESET

        return None

    def detect_dj(self, controller):
        frame = controller.frame()
        if frame.hands.is_empty:
            return None

        if self.fingers_state != ['o', 'o', 'o', 'c', 'c']:
            return

        def filterer(x):
            return x.type in [1]

        fingers = filter(filterer, frame.hands.rightmost.fingers)
        position = fingers[0].bone(1).center
        x = min(150, abs(position[0])) * (-1 if position[0] < 0 else 1)
        z = min(150, abs(position[2])) * (-1 if position[2] < 0 else 1)

        self.action_handler.action_arguments = [x / 1.5, z / 1.5]
        return self.action_handler.EXACT_LOCATION

    def on_frame(self, controller):
        frame = controller.frame()
        frame_reaction = None

        gesture_detections = {
            'swipe': {
                'active': config.UseSwipeToSwitch['enabled'],
                'action': self.detect_swipe
            },
            'tap': {
                'active': config.UseTapToSwitch['enabled'],
                'action': self.detect_tap
            },
            'rotate': {
                'active': config.UseRotateToChangeColor['enabled'],
                'action': self.detect_rotation
            }
        }

        other_detections = {
            'dim': {
                'active': config.UsePalmToDim['enabled'],
                'action': self.detect_dim
            },
            'pinch': {
                'active': config.UsePinchToReset['enabled'],
                'action': self.detect_pinch
            },
            'thumb_out': {
                'active': config.UseThumbOutToReset['enabled'],
                'action': self.detect_thumb_out
            },
            'dj': {
                'active': config.DJChangeColor['enabled'],
                'action': self.detect_dj
            }
        }

        self.set_fingers_state(controller)

        for gesture in frame.gestures():
            for detection in gesture_detections.values():
                if not detection['active']:
                    continue
                result = detection['action'](controller, gesture)
                if result is not None:
                    frame_reaction = result

        for detection in other_detections.values():
            if not detection['active']:
                continue
            result = detection['action'](controller)
            if result is not None:
                frame_reaction = result

        if frame_reaction is not None:
            self.action_handler.handle(frame_reaction)

    def state_string(self, state):
        return self.state_mapping[state]
