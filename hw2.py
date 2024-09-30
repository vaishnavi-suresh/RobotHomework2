import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.base import Base
from viam.components.camera import Camera
from viam.components.encoder import Encoder
from viam.components.movement_sensor import MovementSensor
from viam.services.vision import VisionClient

async def connect():
    opts = RobotClient.Options.with_api_key(
            # Replace "<API-KEY>" (including brackets) with your machine's api key 
        api_key='<API-KEY>',
        # Replace "<API-KEY-ID>" (including brackets) with your machine's api key id
        api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

def findRange (detections):
    adequateConfidence = []
    for detection in detections:
        if detection["confidence"]>0.5:
            adequateConfidence.append(detection)
    bestDetection = adequateConfidence[0]
    bestArea = (bestDetection.x_max-bestDetection.x_min)*(bestDetection.y_max-bestDetection.y_min)
    for d in adequateConfidence:
        area = (d.x_max-d.x_min)*(d.y_max - d.y_min)
        if area > bestArea:
            bestArea = area
            bestDetection =d
    return d

def leftOrRight(detection, midpoint):
    if detection:
        detectionMP = (detection.x_min+detection.x_max)/2
        difference = midpoint-detectionMP
        return difference
    else:
        print("no detection available")
        return None
    
def detectDistance(detection, dist, vel):
    #declare a range for area
    xspan = detection.x_max-detection.x_min
    xspanMin=0.5 *xspan
    xspanMax= xspan
    #will the ranges modify (I haven't coded in python in so long Im so used to C)
    #detect a 2d estimate for the size change of an object
    #move it until it
    if xspan<xspanMin:
        while xspan<xspanMax:
            base.move_straight(dist,vel)

async def connect():
    opts = RobotClient.Options.with_api_key(
        # Replace "<API-KEY>" (including brackets) with your machine's API key
        api_key='<API-KEY>',
        # Replace "<API-KEY-ID>" (including brackets) with your machine's
        # API key ID
        api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address("ADDRESS FROM THE VIAM APP", opts)


async def main():
    machine = await connect()

    print('Resources:')
    print(machine.resource_names)
    
    # Note that the pin supplied is a placeholder. Please change this to a valid pin you are using.
    # local
    local = Board.from_robot(machine, "local")
    local_return_value = await local.gpio_pin_by_name("16")
    print(f"local gpio_pin_by_name return value: {local_return_value}")

    # right
    right = Motor.from_robot(machine, "right")
    right_return_value = await right.is_moving()
    print(f"right is_moving return value: {right_return_value}")

    # left
    left = Motor.from_robot(machine, "left")
    left_return_value = await left.is_moving()
    print(f"left is_moving return value: {left_return_value}")

    # viam_base
    viam_base = Base.from_robot(machine, "viam_base")
    viam_base_return_value = await viam_base.is_moving()
    print(f"viam_base is_moving return value: {viam_base_return_value}")

    # cam
    cam = Camera.from_robot(machine, "cam")
    cam_return_value = await cam.get_image()
    print(f"cam get_image return value: {cam_return_value}")

    # Renc
    renc = Encoder.from_robot(machine, "Renc")
    renc_return_value = await renc.get_position()
    print(f"Renc get_position return value: {renc_return_value}")

    # Lenc
    lenc = Encoder.from_robot(machine, "Lenc")
    lenc_return_value = await lenc.get_position()
    print(f"Lenc get_position return value: {lenc_return_value}")

    # accelerometer
    accelerometer = MovementSensor.from_robot(machine, "accelerometer")
    accelerometer_return_value = await accelerometer.get_linear_acceleration()
    print(f"accelerometer get_linear_acceleration return value: {accelerometer_return_value}")

    # color_detector
    color_detector = VisionClient.from_robot(machine, "color_detector")
    color_detector_return_value = await color_detector.get_properties()
    print(f"color_detector get_properties return value: {color_detector_return_value}")

    # Don't forget to close the machine when you're done!
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
