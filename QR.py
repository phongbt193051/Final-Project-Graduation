import cv2
from pyzbar.pyzbar import decode

cap = cv2.VideoCapture(2, cv2.CAP_V4L2) 

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Giải mã mã QR trong khung hình
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        print(f"Mã QR phát hiện: {obj.data.decode('utf-8')}")

    # Hiển thị khung hình
    cv2.imshow("QR Scanner", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
