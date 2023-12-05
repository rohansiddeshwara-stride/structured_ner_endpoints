from ultralytics import YOLO
import torch


# set image
# image = 'snata.jpg'

# MODEL_NAME = 'keremberke/yolov8m-table-extraction'

def LoadYolo():
    MODEL_NAME = 'Table/model_weights/best.pt'
    model = YOLO(MODEL_NAME)

    model.overrides['conf'] = 0.25  # NMS confidence threshold
    model.overrides['iou'] = 0.45  # NMS IoU threshold
    model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    model.overrides['max_det'] = 1000  # maximum number of detections per image
    return model


def YoloTableDetector(image,MODEL):
    results = MODEL.predict(image)
    result = results[0]
    boxes = result.boxes.xyxy # x1, y1, x2, y2
    scores = result.boxes.conf
    categories = result.boxes.cls
    scores = result.probs # for classification models
    masks = result.masks # for segmentation models
    # print(results[0].boxes)
    # render = render_result(model=model, image=image, result=results[0])
    # render.show()
    box_list=boxes.tolist()
    return box_list




# model_name='keremberke/yolov8m-table-extraction'


# MODEL=LoadYolo(model_name)
# BBOX=YoloTable(image)
# print(BBOX)