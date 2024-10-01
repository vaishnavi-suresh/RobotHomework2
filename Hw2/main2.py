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
        api_key='YOUR_API_KEY',
        api_key_id='YOUR_API_KEY_ID'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

async def getDetections(colorDetector, cam_name, vel, base):
    detections = await colorDetector.get_detections_from_camera(cam_name)
    if not detections:
        for i in range(36):
            await base.spin(10, vel)
            detections = await colorDetector.get_detections_from_camera(cam_name)
            if detections:
                break
    if detections:
        return detections
    else:
        return None

def findRange(detections):
    adequateConfidence = []
    for detection in detections:
        if detection.confidence > 0.5:
            adequateConfidence.append(detection)
    if not adequateConfidence:
        print("No detections with sufficient confidence.")
        return None
    bestDetection = adequateConfidence[0]
    bestArea = (bestDetection.x_max - bestDetection.x_min) * (bestDetection.y_max - bestDetection.y_min)
    for d in adequateConfidence:
        area = (d.x_max - d.x_min) * (d.y_max - d.y_min)
        if area > bestArea:
            bestArea = area
            bestDetection = d
    return bestDetection

def leftOrRight(detection, midpoint):
    if detection:
        detectionMP = (detection.x_min + detection.x_max) / 2
        difference = midpoint - detectionMP
        return difference
    else:
        print("No detection available")
        return None

async def detectDistance(base, detection, dist, vel):
    xspan = detection.x_max - detection.x_min
    xspanMin = 0.5 * xspan
    xspanMax = xspan
    if xspan < xspanMin:
        while xspan < xspanMax:
            await base.move_straight(dist, vel)
            break

async def motion(base, detection, dist, vel, mp):
    while True:
        diff = leftOrRight(detection, mp)
        if diff is not None:
            await base.spin(diff, vel)
            await detectDistance(base, detection, dist, vel)
        else:
            print("No detection available in motion function.")
            break
        break

async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")
    base = Base.from_robot(machine, "viam_base")
    pil_frame = viam_to_pil_image(frame)
    my_detector = VisionClient.from_robot(machine, "color_detector")
    
    vel = 0.8
    dist = 100
    mp = pil_frame.width / 2
    
    detections = await getDetections(my_detector, camera_name, vel, base)
    if detections:
        detection = findRange(detections)
        if detection:
            await motion(base, detection, dist, vel, mp)
        else:
            print("No suitable detection found.")
    else:
        print("No detections found.")

    input("Press Enter to quit")
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())





# import asyncio

# from viam.robot.client import RobotClient
# from viam.components.base import Base
# from viam.components.camera import Camera
# from viam.services.vision import VisionClient
# from viam.media.utils.pil import viam_to_pil_image

# async def connect():
#     opts = RobotClient.Options.with_api_key(
#         api_key='YOUR_API_KEY',
#         api_key_id='YOUR_API_KEY_ID'
#     )
#     return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

# async def getDetections(colorDetector, cam_name, vel, base):
#     detections = await colorDetector.get_detections_from_camera(cam_name)
#     if not detections:
#         for i in range(36):
#             await base.spin(10, vel)
#             detections = await colorDetector.get_detections_from_camera(cam_name)
#             if detections:
#                 break
#     if detections:
#         return detections
#     else:
#         return None

# def findRange(detections):
#     adequateConfidence = []
#     for detection in detections:
#         if detection.confidence > 0.5:
#             adequateConfidence.append(detection)
#     if not adequateConfidence:
#         print("No detections with sufficient confidence.")
#         return None
#     bestDetection = adequateConfidence[0]
#     bestArea = (bestDetection.x_max - bestDetection.x_min) * (bestDetection.y_max - bestDetection.y_min)
#     for d in adequateConfidence:
#         area = (d.x_max - d.x_min) * (d.y_max - d.y_min)
#         if area > bestArea:
#             bestArea = area
#             bestDetection = d
#     return bestDetection

# def leftOrRight(detection, midpoint, frame_width, hfov_degrees):
#     if detection:
#         detectionMP = (detection.x_min + detection.x_max) / 2
#         difference_pixels = midpoint - detectionMP
#         angular_difference = (difference_pixels / frame_width) * hfov_degrees
#         return angular_difference
#     else:
#         print("No detection available")
#         return None

# async def detectDistance(base, detection, vel, vel_param):
#     xspan = detection.x_max - detection.x_min
#     desired_xspan = 100  # Example value; calibrate based on your setup
#     if xspan < desired_xspan:
#         await base.move_straight(vel, vel_param)

# async def motion(base, detection, vel, mp, frame_width, hfov_degrees):
#     try:
#         while True:
#             diff = leftOrRight(detection, mp, frame_width, hfov_degrees)
#             if diff is not None:
#                 angular_adjustment = diff * 0.1  # Example scaling factor; calibrate as needed
#                 await base.spin(angular_adjustment, vel)
#                 await detectDistance(base, detection, vel, vel)
#             else:
#                 print("No detection available in motion function.")
#                 break
#             await asyncio.sleep(0.1)
#     except asyncio.CancelledError:
#         await base.stop()
#         print("Motion task cancelled.")

# async def main():
#     machine = await connect()
#     camera_name = "cam"
#     camera = Camera.from_robot(machine, camera_name)
#     base = Base.from_robot(machine, "viam_base")
#     my_detector = VisionClient.from_robot(machine, "color_detector")
    
#     vel = 0.8
#     dist = 100  # Ensure this aligns with move_straight's expected units
#     frame_width = 1280  # 720p horizontal resolution
#     hfov_degrees = 60  # Example value; adjust based on your camera's actual HFOV
#     mp = frame_width / 2  # 640 pixels
    
#     detections = await getDetections(my_detector, camera_name, vel, base)
#     if detections:
#         detection = findRange(detections)
#         if detection:
#             motion_task = asyncio.create_task(motion(base, detection, vel, mp, frame_width, hfov_degrees))
#         else:
#             print("No suitable detection found.")
#     else:
#         print("No detections found.")
    
#     await asyncio.get_event_loop().run_in_executor(None, input, "Press Enter to quit")
#     if 'motion_task' in locals():
#         motion_task.cancel()
#     await machine.close()

# if __name__ == '__main__':
#     asyncio.run(main())





