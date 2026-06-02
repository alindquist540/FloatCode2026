import RPi.GPIO as GPIO
import time

# Pin definitions (BCM numbering)
SWITCH_1_PIN = 20  # Physical Pin 38
SWITCH_2_PIN = 19  # Physical Pin 35

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Limit Switch Test - Raspberry Pi Zero 2W")
print("=========================================")
print(f"Switch 1 -> GPIO {SWITCH_1_PIN} (Physical Pin 38)")
print(f"Switch 2 -> GPIO {SWITCH_2_PIN} (Physical Pin 35)")
print("Press CTRL+C to exit.\n")

try:
    while True:
        # Read switch states
        # SPST switch pulls signal LOW when closed, so:
        # GPIO.HIGH (1) = Switch OPEN
        # GPIO.LOW  (0) = Switch CLOSED
        switch1_state = "CLOSED" if GPIO.input(SWITCH_1_PIN) == GPIO.LOW else "OPEN"
        switch2_state = "CLOSED" if GPIO.input(SWITCH_2_PIN) == GPIO.LOW else "OPEN"

        print(f"\rSwitch 1 (GPIO 20 | Pin 38): {switch1_state:<6}  |  Switch 2 (GPIO 19 | Pin 35): {switch2_state:<6}", end="")

        time.sleep(0.1)  # Poll every 100ms

except KeyboardInterrupt:
    print("\n\nExiting...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up. Goodbye!")

