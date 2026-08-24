import time
import board
import digitalio
import rotaryio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)


pins = [board.GP10, board.GP9, board.GP8, board.GP7, board.GP2]
keys = []
keycodes = [Keycode.A, Keycode.B, Keycode.C, Keycode.D, Keycode.MUTE]

for pin in pins:
    sw = digitalio.DigitalInOut(pin)
    sw.direction = digitalio.Direction.INPUT
    sw.pull = digitalio.Pull.UP
    keys.append(sw)


encoder = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
last_position = encoder.position
last_states = [True] * len(keys)

while True:
    for i, sw in enumerate(keys):
        current_state = sw.value
        if not current_state and last_states[i]:
            if keycodes[i] == Keycode.MUTE:
                cc.send(ConsumerControlCode.MUTE)
            else:
                kbd.press(keycodes[i])
        elif current_state and not last_states[i]:
            if keycodes[i] != Keycode.MUTE:
                kbd.release(keycodes[i])
        last_states[i] = current_state

    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
    elif position_change < 0:
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
    last_position = current_position

    time.sleep(0.01)
