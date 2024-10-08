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
        for i in range(40):
            await base.spin(18, vel)
            detections = await colorDetector.get_detections_from_camera(cam)
            await asyncio.sleep(2) # added delay for camera
            if detections:
                break
    return detections if detections else None

def findRange(detections):
    bestDetection = max(detections, key=lambda d: (d.x_max - d.x_min) * (d.y_max - d.y_min))
    
    return bestDetection # largest matching color is the target object

async def leftOrRight(detection, midpoint):
    if detection:
        detectionMP = (detection.x_min + detection.x_max) / 2
        print(f"{detectionMP} {midpoint}") 
        if midpoint - midpoint/6 < detectionMP<midpoint+midpoint/6:
            return 0
        if detectionMP <midpoint-midpoint/6:
            return 1
        if detectionMP>midpoint+midpoint/6:
            return -1
        
    else:
        return None

async def detectDistance(pf, detection):
    xspan = detection.x_max - detection.x_min
    yspan = detection.y_max - detection.y_min
    print (xspan)
    print(pf.size[0])
    if xspan > 0.8*pf.size[0] or yspan >0.8*pf.size[1]:
        return 1
    return 0
    

async def motion(pf,myDetector,myCam, base, dist,spinnum, vel, mp):
    while True:
        detections = await getDetections(myDetector, myCam, base, 10)
        detection = findRange(detections)
        LorR = await leftOrRight(detection, mp)
        if LorR ==0:
            await base.move_straight(dist,vel)
        elif LorR ==-1:
            await base.spin(-spinnum,vel)
            await base.move_straight(dist,vel)
        elif LorR ==1:
            await base.spin(spinnum,vel)
            await base.move_straight(dist,vel)
        
        await asyncio.sleep(0.1) 
        status = await detectDistance(pf,detection)
        if status ==1:
            asyncio.get_event_loop().stop()
            break



async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    base = Base.from_robot(machine, "viam_base")
    my_detector = VisionClient.from_robot(machine, "color_detector")
    frame = await camera.get_image(mime_type="image/jpeg")
    pil_frame = viam_to_pil_image(frame)


    
    asyncio.create_task(motion(pil_frame,my_detector,camera_name, base, 150,15, 500, pil_frame.size[0]/2))  # Adjust parameters as needed
    print("Motion task started. Press Enter to quit.")
    await asyncio.get_event_loop().run_in_executor(None, input, "")

        


    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
