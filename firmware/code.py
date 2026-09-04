import time
import board
import digitalio
import rotaryio
import busio
import displayio
import terminalio
import usb_hid
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode


displayio.release_displays()


i2c = busio.I2C(board.GP5, board.GP4)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 32
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)


splash = displayio.Group()
display.root_group = splash


header_area = label.Label(terminalio.FONT, text="KITTYPAD :3", color=0xFFFFFF, x=0, y=5)
splash.append(header_area)


status_area = label.Label(terminalio.FONT, text="Ready!", color=0xFFFFFF, x=0, y=20)
splash.append(status_area)



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

# Encoder on GP0 and GP1
encoder = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
last_position = encoder.position
last_states = [True] * len(keys)

while True:
    # Key Press Handler
    for i, sw in enumerate(keys):
        current_state = sw.value
        if not current_state and last_states[i]:
            if keycodes[i] == Keycode.MUTE:
                cc.send(ConsumerControlCode.MUTE)
                status_area.text = "Action: Mute"
            else:
                kbd.press(keycodes[i])
                status_area.text = f"Key {i+1} Pressed"
        elif current_state and not last_states[i]:
            if keycodes[i] != Keycode.MUTE:
                kbd.release(keycodes[i])
        last_states[i] = current_state


    current_position = encoder.position
    position_change = current_position - last_position
    if position_change > 0:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        status_area.text = "Vol: + UP"
    elif position_change < 0:
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        status_area.text = "Vol: - DOWN"
    last_position = current_position

    time.sleep(0.01)
