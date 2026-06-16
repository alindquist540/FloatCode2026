#!/usr/bin/env python3
import serial
import time

COMMANDS = {
    'E':    'Enable motor',
    'S':    'Disable motor',
    'F200': 'Forward 200 steps (1 rev)',
    'F400': 'Forward 400 steps (2 rev)',
    'B200': 'Backward 200 steps',
    'R':    'Full rotation',
    'X60':  'Set speed 60 RPM',
    'X30':  'Set speed 30 RPM',
}

def run_test_sequence(ser):
    print("\n--- Automated Test Sequence ---")
    sequence = ['E', 'X60', 'F200', 'F400', 'B200', 'R', 'X30', 'F200', 'S']
    for cmd in sequence:
        print(f"\n[{cmd}] {COMMANDS.get(cmd, '')}")
        ser.write(f"{cmd}\n".encode('utf-8'))
        line = ser.readline().decode('utf-8').rstrip()
        print(f"  Arduino: {line}")
        time.sleep(1.5)
    print("\n--- Test complete ---\n")

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    time.sleep(2)  # wait for Arduino to boot

    print("Stepper Motor Test — A4988 via Arduino")
    print("Commands: F<steps>, B<steps>, X<rpm>, E, S, R, T (auto-test), Q (quit)")

    while True:
        cmd = input("\nCommand > ").strip().upper()
        if not cmd:
            continue
        if cmd == 'Q':
            print("Bye.")
            break
        if cmd == 'T':
            run_test_sequence(ser)
            continue

        ser.write(f"{cmd}\n".encode('utf-8'))
        line = ser.readline().decode('utf-8').rstrip()
        print(f"  Arduino: {line}")
