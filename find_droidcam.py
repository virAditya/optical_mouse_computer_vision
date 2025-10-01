import cv2

print("🔍 Finding DroidCam camera...")
print("-" * 50)

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            print(f"✅ Camera {i}: {width}x{height} pixels")
            
            # Show 2-second preview
            cv2.imshow(f"Camera {i} - Press any key", frame)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
            
        cap.release()
    else:
        print(f"❌ Camera {i}: Not available")

print("-" * 50)
print("📝 Use the DroidCam camera number in config.yaml")
