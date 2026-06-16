import time
import ms5837
import csv
from datetime import datetime
import serial
import sys
import RPi.GPIO as GPIO

SWITCH_1_PIN = 20  # Physical Pin 38
SWITCH_2_PIN = 19  # Physical Pin 35

csv_data = "Float_Depth_Log.csv"

with open(csv_data, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Timestamp", "Depth (m)", "Pressure (Pa)"])

def read_depth(sensor):
    # Trigger a new I2C read; returns True on success
    if not sensor.read():
        return None, None
    # You can either use sensor.depth() (which applies default density)
    # or compute depth from an adjusted pressure:
    return sensor.depth(), sensor.pressure()

if __name__ == "__main__":
    num_read = 5
    # 1) Use the 02BA class, not the generic MS5837:
    sensor = ms5837.MS5837_02BA()
    if not sensor.init():
        raise RuntimeError("Could not initialize MS5837_02BA")

 # 2) (Optional) If you’re in saltwater, override the default density:
 # sensor.setFluidDensity(1029.0)

  # 3) Calibrate zero at the surface:
    time.sleep(5)              # let sensor stabilize
    if not sensor.read():
        raise RuntimeError("Failed to read for zero-offset")
    surface_pressure = sensor.pressure()
    surface_depth = 0

    print(f"Zero-surface pressure = {surface_pressure:.1f} mbar")
    print(f"Zero-surface depth = {surface_depth:.1f} m")

    time.sleep(5)               # give time to put sensor in water

GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SWITCH_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PORT      = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = 9600

def send_command(ser, cmd):
    ser.write((cmd + "\n").encode("utf-8"))
    time.sleep(0.1)

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

    # Start moving forward
    direction = "F"  # F = forward, B = backward
    send_command(ser, "E")
    send_command(ser, direction)
    print("Motor started moving forward")

# Start reading depth in water
    try: 
        while True:
            Fluid_p = 997        # fluid density in kg/m^3
    
            switch1_state = "CLOSED" if GPIO.input(SWITCH_1_PIN) == GPIO.LOW else "OPEN"
            switch2_state = "CLOSED" if GPIO.input(SWITCH_2_PIN) == GPIO.LOW else "OPEN"
    
            if sensor.read():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                adj_pressure = sensor.pressure() - surface_pressure
                depth_m = (adj_pressure * 100) / (Fluid_p * 9.80665)    # 9.80665 is standard gravity
    
                print(f"{timestamp}")    # time
                print(f"Pressure: {adj_pressure:.3f} mbar")    # pressure just from water
                print(f"Depth: {depth_m:.3f} m")       # accounts for atm pressure
    
                with open(csv_data, mode='a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([timestamp, round(depth_m, 3), round(adj_pressure, 2)])
            
            else:
                print("I²C read failure")
    
            time.sleep(0.5)  # Wait 0.5 seconds before next reading
                
            if switch1_state == "CLOSED" and direction == "F":
                print("Switch 1 triggered — reversing to backward!")
                direction = "B"
                send_command(ser, "S")   # stop first
                time.sleep(0.3)
                send_command(ser, "B")   # go backward
                time.sleep(0.5)          # debounce delay
    
            if switch2_state == "CLOSED" and direction == "B":
                print("Switch 2 triggered — reversing to forward!")
                direction = "F"
                send_command(ser, "S")   # stop first
                time.sleep(0.3)
                send_command(ser, "F")   # go forward
                time.sleep(0.5)          # debounce delay
    
                # Read and print any messages from Arduino
            if ser.in_waiting:
                message = ser.readline().decode("utf-8").strip()
                if message:
                    print(f"Arduino: {message}")
    
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("Measurement stopped.")
        send_command(ser, "S")
        
    finally:
        ser.close()
        GPIO.cleanup()
        print("Cleanup done.")
        
if __name__ == "__main__":
    main()
