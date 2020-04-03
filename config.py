LeapMotionSDKLibrary = 'lib'
PrintLog = False
ChangeColorSpeed = {
    'value': 2,
    'verbose_name': "How fast light's color should change"
}
UseTapToSwitch = {
    'enabled': True,
    'verbose_name': "Tap to switch light"
}
UseSwipeToSwitch = {
    'enabled': True,
    'verbose_name': "Swipe to switch light"
}
UseRotateToChangeColor = {
    'enabled': True,
    'verbose_name': "Rotate to change color"
}
UsePalmToDim = {
    'enabled': True,
    'verbose_name': "Move hand up and down to dim the light"
}
UsePinchToReset = {
    'enabled': False,
    'verbose_name': "Pinch to reset light color"
}
UseThumbOutToReset = {
    'enabled': True,
    'verbose_name': "Thumb out to reset light color"
}
DJChangeColor = {
    'enabled': True,
    'verbose_name': "Change colors like a DJ"
}

prompts = [
    UseTapToSwitch,
    UseSwipeToSwitch,
    UseRotateToChangeColor,
    UsePalmToDim,
    UsePinchToReset,
    UseThumbOutToReset,
    DJChangeColor
]
