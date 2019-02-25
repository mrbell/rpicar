from inputs import devices
from inputs import get_gamepad

while True:
    events = get_gamepad()

    for event in events:
        if (
            event.ev_type != 'Sync' and 
            not (event.code == 'ABS_X' and abs(event.state) < 2000) and 
            not (event.code == 'ABS_Y' and abs(event.state) < 2000) and 
            not (event.code == 'ABS_RX' and abs(event.state) < 2000) and 
            not (event.code == 'ABS_RY' and abs(event.state) < 2000) 
        ):
            print(event.ev_type, event.code, event.state)
