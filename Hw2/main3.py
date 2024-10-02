import asyncio
import time
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.base import Base
from viam.components.camera import Camera
from viam.components.encoder import Encoder
from viam.components.movement_sensor import MovementSensor
from viam.services.vision import VisionClient
from viam.media.utils.pil import pil_to_viam_image, viam_to_pil_image
import threading

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='i11ph4btwvdp1kixh3oveex92tmvdtx2',
        api_key_id='8b19e462-949d-4cf3-9f7a-5ce0854eb7b8'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

def leftOrRight(detection, image_width):
    detection_center = (detection.x_min + detection.x_max) / 2
    image_center = image_width / 2
    difference = detection_center - image_center  #right is +, left is -
    # Normalize the difference to a range between -0.5 and 0.5
    normalized_diff = difference / image_width
    return normalized_diff

async def search_for_object(base, vision_service, camera_name, spin_speed): //increments rotationally horizontally
    print("Object not detected. Initiating search.")
    rotation_increment = 45  # Degrees turned each rotation 
    total_rotation = 0
    max_rotation = 360  #360 is max degrees
    detections = None

    while total_rotation < max_rotation and not detections:
        await base.spin(rotation_increment, spin_speed)
        total_rotation += rotation_increment
        print(f"Spun {total_rotation} degrees.")
        await asyncio.sleep(2)  # so that camera has time to warm up and take captures
        detections = await vision_service.get_detections_from_camera(camera_name)
        if detections:
            print("Object found during search.")
            break
    if not detections:
        print("Object not found after full rotation.")
    return detections

async def track_object(base, detection, image_width, forward_speed): //uses leftOrRight fn
    normalized_diff = leftOrRight(detection, image_width)
    threshold = 0.05 
    print(f"Normalized difference: {normalized_diff}")
    if abs(normalized_diff) > threshold:
        angle = normalized_diff * 60 
        print(f"Turning rover by {angle} degrees to center the object.")
        await base.spin(angle, 30) 
        await asyncio.sleep(2)  # camera lag
    else:
        print("Object is centered.")

    object_width = detection.x_max - detection.x_min
    size_threshold = image_width * 0.5  # this to understand the depth of the object
    print(f"Object width: {object_width}, Size threshold: {size_threshold}")

    if object_width < size_threshold:
        print("Object is far. Moving forward.")
        await base.move_straight(0.3, forward_speed)  
        await asyncio.sleep(2)
    else:
        print("Object is close enough.")

async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    base = Base.from_robot(machine, "viam_base")
    my_detector = VisionClient.from_robot(machine, "color_detector")

    try:
        while True:
            detections = await my_detector.get_detections_from_camera(camera_name)
            if detections:
                detection = max(detections, key=lambda d: d.confidence)
                image = await camera.get_image()
                image_width = image.width
                await track_object(base, detection, image_width, forward_speed=0.1)
            else:
                detections = await search_for_object(base, my_detector, camera_name, spin_speed=30)
                if not detections:
                    print("Object not found after search. Waiting before next attempt.")
                    await asyncio.sleep(2) 
            await asyncio.sleep(1) 
    except KeyboardInterrupt:
        print("Stopping the rover.")
    finally:
        await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
