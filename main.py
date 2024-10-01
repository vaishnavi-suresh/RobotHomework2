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
            # Replace "<API-KEY>" (including brackets) with your machine's api key 
        api_key='i11ph4btwvdp1kixh3oveex92tmvdtx2',
        # Replace "<API-KEY-ID>" (including brackets) with your machine's api key id
        api_key_id='8b19e462-949d-4cf3-9f7a-5ce0854eb7b8'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

def getDetections(colorDetector,cam,vel):
    detections =  colorDetector.get_detections_from_camera(cam)
    if not detections:
        for i in range(36):
            base.spin(10,vel)
            detections =  colorDetector.get_detections_from_camera(cam)
            if detections:
                break
    if detections:
        return detections
    else:
        return None


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

def motion(detection, dist, vel, mp):
    while True:
        diff = leftOrRight(detection, mp)
        base.spin(diff, vel)
        detectDistance(detection, dist,vel)


async def main():
    #following straight from tutorial, edit
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")
    base = Base.from_robot(machine, "viam_base")
    pil_frame = viam_to_pil_image(frame)
    my_detector = VisionClient.from_robot(machine, "color_detector") #change name to match color detector
    

    #find detections
    #then find range
    #save detection
    #then use a daemon thread to find if it is left or right, rotate that much in that direction, find distance, move forward that much
    #press enter to quit
    detections = getDetections(my_detector,camera,0.8)
    detection = findRange(detections)
    threading.Thread(target=motion, daemon=True).start()
    input("Press enter to quit")
    
    # Don't forget to close the machine when you're done!
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())
