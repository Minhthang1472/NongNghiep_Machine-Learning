import os
import sys
import numpy as np
import tensorflow as tf
from keras.preprocessing import image

# Tắt thông báo rác của TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

def predict_image(img_path):
    model_path = 'fruit_model.h5'
    label_path = 'labels.txt'

    if not os.path.exists(model_path):
        print("Lỗi: Không tìm thấy fruit_model.h5")
        return
    if not os.path.exists(img_path):
        print(f"Lỗi: Không tìm thấy ảnh {img_path}")
        return

    # Load model & labels
    model = tf.keras.models.load_model(model_path)
    with open(label_path, 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]

    # Load image
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    # Phân tích
    predictions = model.predict(img_array, verbose=0)
    best_idx = np.argmax(predictions[0])
    predicted_label = labels[best_idx]

    # Phân tách Nhãn
    loai_qua = "Chưa rõ"
    do_chin = "Chưa rõ"

    if "Apple" in predicted_label: loai_qua = "Táo"
    elif "Banana" in predicted_label: loai_qua = "Chuối"
    elif "Grape" in predicted_label: loai_qua = "Nho"
    elif "Orange" in predicted_label: loai_qua = "Cam"
    elif "Guava" in predicted_label: loai_qua = "Ổi"
    elif "Pomegranate" in predicted_label: loai_qua = "Lựu"
    elif "Strawberry" in predicted_label: loai_qua = "Dâu Tây"
        
    if "Ripe" in predicted_label and "Unripe" not in predicted_label: do_chin = "Chín"
    elif "Unripe" in predicted_label: do_chin = "Xanh"
    elif "Rotten" in predicted_label: do_chin = "Hư hỏng"

    prob_chin, prob_xanh, prob_hu_hong = 0.0, 0.0, 0.0
    for i, label in enumerate(labels):
        if "Ripe" in label and "Unripe" not in label:
            prob_chin += predictions[0][i] * 100
        elif "Unripe" in label:
            prob_xanh += predictions[0][i] * 100
        elif "Rotten" in label:
            prob_hu_hong += predictions[0][i] * 100

    if do_chin == "Chín":
        confidence = prob_chin
    elif do_chin == "Xanh":
        confidence = prob_xanh
    else:
        confidence = prob_hu_hong
        
    if confidence > 99.9: confidence = 99.9

    # Tiếng Việt hoàn toàn
    if do_chin == "Hư hỏng":
        ket_luan = f"TỪ CHỐI ❌ ({loai_qua} đã hỏng, yêu cầu cách ly để tránh nấm mốc)"
        status_dot = "● HƯ HỎNG (ROTTEN)"
    elif do_chin == "Xanh":
        ket_luan = f"CẢNH BÁO ⚠️ (Nồng độ đường (Brix) chưa đạt ngưỡng)"
        status_dot = "● QUẢ XANH (UNRIPE)"
    elif do_chin == "Chín":
        if confidence >= 75.0:
            ket_luan = f"ĐẠT CHUẨN ✅ (Độ đường và vitamin đạt mức tối ưu)"
            status_dot = "● CHÍN ĐẠT CHUẨN"
        else:
            ket_luan = "KIỂM TRA THỦ CÔNG ⚠️ (Độ tin cậy của AI thấp)"
            status_dot = "● CHÍN (THIẾU TIN CẬY)"
    else:
        ket_luan = "LỖI HỆ THỐNG ❌"
        status_dot = "● LỖI (ERROR)"

    print("\n" + "="*55)
    print(" 🍊 KẾT QUẢ KIỂM ĐỊNH TRÁI CÂY (AI SCANNER V4.0)")
    print("="*55)
    print(f" [IMG] File ảnh    : {os.path.basename(img_path)}")
    print(f" [QA]  Loại quả    : {loai_qua.upper()}")
    print(f" [QA]  Trạng thái  : {status_dot}")
    print(f" [QA]  Độ tin cậy  : {confidence:.2f}%")
    print(f" [QA]  KẾT LUẬN    : {ket_luan}")
    print("-" * 55)
    print(" 📊 XÁC SUẤT CHI TIẾT THEO TRẠNG THÁI:")
    print(f"    - Chín         : {prob_chin:>6.2f}%")
    print(f"    - Xanh         : {prob_xanh:>6.2f}%")
    print(f"    - Hư hỏng      : {prob_hu_hong:>6.2f}%")
    print("="*55 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Cú pháp: python predict.py <đường_dẫn_ảnh>")
    else:
        predict_image(sys.argv[1])
