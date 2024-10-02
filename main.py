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
from viam.media.utils.pil import pil_to_viam_image, viam_to_pil_image
import threading
import time

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='i11ph4btwvdp1kixh3oveex92tmvdtx2',
        api_key_id='8b19e462-949d-4cf3-9f7a-5ce0854eb7b8'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

async def getDetections(colorDetector, cam, base, vel):
    detections = await colorDetector.get_detections_from_camera(cam)
    if not detections:
        for i in range(5):
            await base.spin(72, vel)
            print ("spin in progress")
            detections = await colorDetector.get_detections_from_camera(cam)
            if detections:
                break
    return detections if detections else None

def findRange(detections):
    adequateConfidence = [d for d in detections if d.confidence > 0.1]
    if not adequateConfidence:
        return None
    bestDetection = max(adequateConfidence, key=lambda d: (d.x_max - d.x_min) * (d.y_max - d.y_min))
    
    return bestDetection

def leftOrRight(detection, midpoint):
    if detection:
        detectionMP = (detection.x_min + detection.x_max) / 2
        print(f"{detectionMP} {midpoint}")
        difference = midpoint - detectionMP
        if difference == 0:
            return None
        print("detection found")
        return difference
    else:
        print("no detection available")
        return None
    
async def detectDistance(detection, base, dist, vel):
    xspan = detection.x_max - detection.x_min
    print("running detect distance")
    xspanMin = 0.5 * xspan
    xspanMax = xspan
    if xspan < xspanMin:
        print("object small")
        while xspan < xspanMax:
            base.move_straight(dist, vel)
            # You might want to update the detection here to get the new xspan

async def motion(detection, base, dist, vel, mp):
    while True:
        diff = leftOrRight(detection, mp)
        print("motion loop running")

        if diff is not None:
            print(diff)
            await base.spin(diff, vel)
            print ("success")
            time.sleep(1)
        await detectDistance(detection, base, dist, vel)
        await asyncio.sleep(0.1)  # Add a small delay to prevent tight looping

async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    base = Base.from_robot(machine, "viam_base")
    my_detector = VisionClient.from_robot(machine, "color_detector")

    detections = await getDetections(my_detector, camera_name, base, 1)
    detection = findRange(detections)

    if detection:
        asyncio.create_task(motion(detection, base, 10, 1, 0.5))  # Adjust parameters as needed
        print("Motion task started. Press Enter to quit.")
        await asyncio.get_event_loop().run_in_executor(None, input, "")
    else:
        print("No detections found.")

    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
