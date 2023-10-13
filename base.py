from ultralytics import YOLO
import cv2
from sort.sort import*
from matplotlib import pyplot as plot
from utils import *


results={}
auto_trackers=Sort()
#loading models
objectModel=YOLO('./yolov8n.pt')
license_plate_detector=YOLO('./license_plate_detector.pt')

#loading video
cap=cv2.VideoCapture('./smpl.mp4')


#vehicles list with class Id
vehicles=[2,3,5,7]

#reading frames
frameNumber=-1
ret= True
while ret :
    frameNumber+=1
    ret,frame=cap.read()
    
    if ret and frameNumber>250 and frameNumber<280:
        results[frameNumber] = {}
        #detect vehicles
        detections=objectModel(frame)[0]
        allVehiclesInFrame=[]
        for detection in detections.boxes.data.tolist():
            x1,y1,x2,y2,score,class_id=detection
            if int(class_id) in vehicles:
                allVehiclesInFrame.append([x1,y1,x2,y2,score,class_id])
           
        
        #tracking vehicles
        tracking_id=auto_trackers.update(np.asarray(allVehiclesInFrame))

        # detect license plate
        license_plates=license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1,y1,x2,y2, score,class_id=license_plate

            
            xv1,yv1,xv2,yv2,car_id=get_vehicle(license_plate,tracking_id)

            license_plate_cropped=frame[int(y1):int(y2),int(x1):int(x2), : ]

            license_plate_cropped_gray=cv2.cvtColor(license_plate_cropped,cv2.COLOR_BGR2GRAY)
            _,license_plate_threshold=cv2.threshold(license_plate_cropped_gray,64,255,cv2.THRESH_BINARY_INV)


            # rect=cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),color=(255,0,0))
            # rect=cv2.rectangle(rect,(int(xv1),int(yv1)),(int(xv2),int(yv2)),color=(0,0,255))
            # plot.imsave(f'${frameNumber}.jpg',license_plate_cropped_gray)
            # # plot.imsave(f'${frameNumber}.jpg',rect)


            license_plate_text,license_plate_text_score=read_license_plate_text(license_plate_threshold)

            if license_plate_text is not None:
                results[frameNumber][car_id]={'car':{'bbox':[xv1,yv1,xv2,yv2]},
                                            'license_plate':{'bbox':[x1,y1,x2,y2],
                                                             'text':license_plate_text,
                                                             'bbox_score':score,
                                                             'text_score':license_plate_text_score}}

write_csv(results,'./test.csv')