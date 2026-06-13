"""
Raspberry Pi -> Arduino -> A4988 Stepper Motor Driver Test
Communication: Serial (USB/UART)

Commands sent to Arduino:
  F<steps>  - Move Forward N steps  (e.g. "F200")
  B<steps>  - Move Backward N steps (e.g. "B200")
  S         - Stop / disable motor
  E         - Enable motor
  R         - Full rotation (200 steps forward)
  X<speed>  - Set speed in RPM (e.g. "X60")

Usage:
  python3 pi_stepper_control.py
  or specify port:
  python3 pi_stepper_control.py /dev/ttyUSB0
"""

import serial
import time
import sys


# ── Configuration ─────────────────────────────────────────────────────────────
PORT      = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BAUD_RATE = 9600
TIMEOUT   = 2  # seconds
# ──────────────────────────────────────────────────────────────────────────────


def send_command(ser: serial.Serial, cmd: str) -> str:
    """Send a command string and return the Arduino's response."""
    ser.write((cmd + "\n").encode("utf-8"))
    time.sleep(0.05)
    response = ser.readline().decode("utf-8").strip()
    return response


def run_test_sequence(ser: serial.Serial):
    """Run a basic automated test sequence."""
    print("\n─── Automated Test Sequence ───")

    tests = [
        ("E",    "Enable motor"),
        ("X60",  "Set speed to 60 RPM"),
        ("F200", "Move FORWARD 200 steps (1 revolution)"),
        ("F400", "Move FORWARD 400 steps (2 revolutions)"),
        ("B200", "Move BACKWARD 200 steps"),
        ("R",    "Full rotation (shortcut)"),
        ("X30",  "Set speed to 30 RPM (slower)"),
        ("F200", "Move FORWARD 200 steps at low speed"),
        ("S",    "Disable motor"),
    ]

    for cmd, description in tests:
        print(f"\n  [{cmd}] {description}")
        response = send_command(ser, cmd)
        print(f"       Arduino: {response}")
        time.sleep(1.5)   # wait for motion to complete

    print("\n─── Test sequence complete ───\n")


def interactive_mode(ser: serial.Serial):
    """Let the user type commands manually."""
    print("\n─── Interactive Mode ───")
    print("Commands:")
    print("  F<steps>  e.g. F200  — move forward")
    print("  B<steps>  e.g. B200  — move backward")
    print("  X<rpm>    e.g. X60   — set speed")
    print("  E         — enable motor")
    print("  S         — stop / disable motor")
    print("  R         — one full rotation")
    print("  T         — run automated test sequence")
    print("  Q         — quit\n")

    while True:
        try:
            cmd = input("Command > ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not cmd:
            continue
        if cmd == "Q":
            print("Goodbye.")
            break
        if cmd == "T":
            run_test_sequence(ser)
            continue

        response = send_command(ser, cmd)
        print(f"  Arduino: {response}")


def main():
    print(f"Connecting to Arduino on {PORT} at {BAUD_RATE} baud…")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port — {e}")
        sys.exit(1)

    # Arduino resets on serial connect; give it time to boot
    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!\n")

    # Read Arduino's startup message if any
    startup = ser.readline().decode("utf-8").strip()
    if startup:
        print(f"Arduino says: {startup}")

    interactive_mode(ser)
    ser.close()


if __name__ == "__main__":
    main()
