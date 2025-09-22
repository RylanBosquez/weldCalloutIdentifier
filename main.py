import os
import cv2
import torch
from ultralytics import YOLO
from torchvision.ops import nms

# Define paths for input images and trained model
exampleImageFolder = './assets/weldExamples'
modelPath = './assets/weldIdentifier.pt'

# Clear the terminal screen (Windows only)
os.system('cls')

# Load the trained YOLO model
model = YOLO(modelPath)

# Loop through all images in the example folder
for file in os.listdir(exampleImageFolder):
    imagePath = os.path.join(exampleImageFolder, file)
    image = cv2.imread(imagePath)

    # Run inference on the image
    results = model(image)

    for result in results:
        boxes = result.boxes  # Detected bounding boxes
        clsNames = result.names  # Class name mapping

        boxData = []  # Store filtered boxes with confidence > 0.5
        for box in boxes:
            conf = float(box.conf)
            if conf > 0.5:
                # Extract box coordinates and class ID
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                boxData.append([x1, y1, x2, y2, conf, int(box.cls)])

        # Apply Non-Maximum Suppression to remove overlapping boxes
        if boxData:
            boxTensor = torch.tensor([b[:4] for b in boxData], dtype=torch.float32)
            scores = torch.tensor([b[4] for b in boxData], dtype=torch.float32)
            indices = nms(boxTensor, scores, iou_threshold=0.5)

            # Draw retained boxes and labels on the image
            for idx in indices:
                x1, y1, x2, y2, conf, clsId = boxData[idx]
                clsName = clsNames[clsId]
                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
                cv2.putText(image, f'{clsName} {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the image with annotations
    cv2.imshow(file.split('.')[0], image)

    # Save the annotated image to output folder
    cv2.imwrite(f'./assets/identified/{file}', image)

    # Wait for key press and close window
    cv2.waitKey(0)
    cv2.destroyAllWindows()
