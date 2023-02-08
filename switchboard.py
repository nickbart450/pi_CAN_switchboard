# switchboard.py
"""
Main loop that listens for input from 3 switch board and outputs CAN stream current states.
"""

from collections import namedtuple
import argparse
import time
import os

# Raspberry Pi
from gpiozero import Button

# CAN bus
import can

# Raspberry Pi switch configuration
SWITCHES = {
    'switch_a': Button(14),  # pin assignment, defaults to pull-up (switching to ground)
    'switch_b': Button(18),
    'switch_c': Button(12),
}


def init_canbus():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 txqueuelen 100000')
    os.system('sudo ifconfig can0 up')

    can_dev = can.interface.Bus(channel='can0', bustype='socketcan')
    return can_dev


def read_switch(switch):
    button = SWITCHES[switch]    
    if button.value:
        # print("The button is pressed")
        state = 1
    else:
        state = 0
    return state


def read_switch_states():
    states = namedtuple('switches', ['a', 'b', 'c'])
    states.a = read_switch('switch_a')
    states.b = read_switch('switch_b')
    states.c = read_switch('switch_c')

    return states


def main():
    start = time.time_ns()
    c = 0
    can_msg_send_count = 0
    
    while True:
        switch_states = read_switch_states()
        print('Switch States: ', switch_states.a, switch_states.b, switch_states.c)

        if not args.disable_can:
            msg = can.Message(arbitration_id=0x123,
                              data=[switch_states.a, switch_states.b, switch_states.c, 111, 111, 111, 111, 111],
                             )
            # can_device.send(msg)
            print('CAN message: ', msg)
            can_msg_send_count += 1
            print('CAN messages sent: ', can_msg_send_count)
        
        time.sleep(0.01)
        c += 1
        elapsed = float(time.time_ns()-start)/1000000  # msec
        # print('msec/loop: ', round(elapsed/c, 2))
        print('Hz: ', round(c/(elapsed/1000), 2))


if __name__ == '__main__':
    print('Starting Switchboard')

    parser = argparse.ArgumentParser(
        prog='CAN Switchboard',
        description='Continuously transmits Raspberry Pi input switch states on CAN-bus',
    )
    parser.add_argument('--disable_can', action='store_true', help='Deactivate CAN message creation and sending in the main loop for testing.')
    args = parser.parse_args()

    if not args.disable_can:
        can_device = init_canbus()
    main()
    # read_switch('switch_a')
