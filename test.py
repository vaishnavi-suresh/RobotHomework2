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
import threading
import time

async def main():
    #following straight from tutorial, edit
    machine = await connect()
    base = Base.from_robot(machine, "my_base")
    camera_name = "<camera-name>"
    camera = Camera.from_robot(machine, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")
    base = Base.from_robot(machine, "my_base")
    camera_name = "<camera-name>"
    camera = Camera.from_robot(machine, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")
    pil_frame = viam_to_pil_image(frame)
    my_detector = VisionClient.from_robot(machine, "my_color_detector") #change name to match color detector
    

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
