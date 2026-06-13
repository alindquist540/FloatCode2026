import serial
import time
import sys

PORT      = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = 9600

def main():
    print(f"Connecting to Arduino on {PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port — {e}")
        sys.exit(1)

    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!")
    print("Press Ctrl+C to stop\n")

    # Send enable command to start rotating
    ser.write(("E\n").encode("utf-8"))
    time.sleep(0.1)
    response = ser.readline().decode("utf-8").strip()
    print(f"Arduino: {response}")

    try:
        while True:
            # Read and print any messages from Arduino
            if ser.in_waiting:
                message = ser.readline().decode("utf-8").strip()
                if message:
                    print(f"Arduino: {message}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping motor...")
        ser.write(("S\n").encode("utf-8"))
        time.sleep(0.5)
        print("Motor stopped.")
        ser.close()

if __name__ == "__main__":
    main()
