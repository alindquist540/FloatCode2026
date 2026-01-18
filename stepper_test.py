from stepper_motors_juanmf1 import (GenericStepper, DRV8825MotorDriver, ExponentialAcceleration, DynamicDelayPlanner, DynamicNaviation)
from time import sleep

class StepperMotor:

  def __init__(self):
    self.motor = StepperMotor.setupDriver(directionGpioPin=31, stepGpioPin=29)
    self.motorPosition = 0

    self.move(motorDelta=100)
    sleep(0.05)

    # While still moving, send contradictory order to arm. It should gracefully
    # stop and speed back up in opposite direction
    self.move(motorDelta=-100)

  def motorPositionListener(self, currentPosition, targetPosition, direction):
    self.motorPosition = currentPosition

  def move(self, motorDelta):
    if motorDelta != 0:
      if motorDelta > 0:
        self.motor.stepClockwise(motorDelta, self.motorPositionListener)
      else:
        self.motor.stepCounterClockwise(motorDelta, self.motorPositionListener)

  @staticmethod
  def setupDriver(*, directionGpioPin, stepGpioPin):
    stepperMotor = GenericStepper(maxPps=1500, minPps=150) #chatgpt math said 1500 for safe value, 150 from example
    delayPlanner = DynamicDelayPlanner()
    navigation = DynamicNavigation()

    acceleration = ExponentialAcceleration(stepperMotor, delayPlanner)
    return DRV8825MotorDriver(stepperMotor, acceleration, directionGpioPin, stepGpioPin, navigation)
