import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image # type: ignore
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

IMG_SIZE = (224, 224)

def predict_image(img_path):
    model_path = 'fruit_model.h5'
    label_path = 'labels.txt'

    if not os.path.exists(model_path):
        print("[LỖI] Không tìm thấy file 'fruit_model.h5'. Hãy chạy train.py trước!")
        return
    if not os.path.exists(img_path):
        print(f"[LỖI] Không tìm thấy ảnh: {img_path}")
        return

    # Ẩn log rác
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Đọc model và nhãn
    model = tf.keras.models.load_model(model_path)
    with open(label_path, 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]

    # Xử lý ảnh đầu vào
    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0 # Chuẩn hóa giống lúc train

    # Dự đoán
    predictions = model.predict(img_array, verbose=0)
    best_idx = np.argmax(predictions[0])
    predicted_class_idx = best_idx
    confidence = predictions[0][best_idx] * 100

    # In kết quả đẹp mắt
    # Chuyển đổi nhãn tiếng Anh sang tiếng Việt cho đẹp
    predicted_label = labels[predicted_class_idx]
    
    loai_qua = "Không rõ"
    do_chin = "Không rõ"
    
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

    # Cơ chế ra quyết định tự động CHUYÊN SÂU THEO TỪNG LOẠI QUẢ
    if do_chin == "Hư hỏng":
        ket_luan = f"KHÔNG ĐƯỢC SỬ DỤNG ❌ ({loai_qua} đã hỏng, cần loại bỏ ngay để tránh lây nấm mốc)"
    elif do_chin == "Xanh":
        if loai_qua == "Chuối":
            ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ⚠️ (Chuối còn xanh, cần ủ thêm 2-3 ngày)"
        elif loai_qua == "Cam":
            ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ⚠️ (Cam còn xanh, vắt nước sẽ rất chua)"
        elif loai_qua == "Ổi":
            ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ⚠️ (Ổi xanh, thịt cứng và chát)"
        elif loai_qua == "Táo":
            ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ⚠️ (Táo xanh, độ đường chưa đạt chuẩn)"
        elif loai_qua == "Dâu Tây":
            ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ⚠️ (Dâu tây chưa chín, vị chua gắt)"
        else:
            ket_luan = f"KHÔNG ĐƯỢC SỬ DỤNG ⚠️ ({loai_qua} còn xanh, chưa đạt tiêu chuẩn thu hoạch)"
    elif do_chin == "Chín":
        if confidence >= 75.0:
            if loai_qua == "Chuối":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Chuối chín vàng, thích hợp ăn tươi hoặc làm bánh)"
            elif loai_qua == "Cam":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Cam chín mọng nước, lượng vitamin C cao nhất)"
            elif loai_qua == "Nho":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Nho chín, độ ngọt brix cao, thích hợp ép rượu/ăn tươi)"
            elif loai_qua == "Lựu":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Lựu chín đỏ, hạt mọng nước)"
            elif loai_qua == "Dâu Tây":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Dâu tây chín mọng, nên sử dụng ngay để tránh dập nát)"
            elif loai_qua == "Táo":
                ket_luan = "ĐƯỢC SỬ DỤNG ✅ (Táo thơm, giòn ngọt, đạt chuẩn xuất khẩu)"
            else:
                ket_luan = f"ĐƯỢC SỬ DỤNG ✅ ({loai_qua} chín đẹp, đạt chuẩn an toàn)"
        else:
            ket_luan = "CẦN KIỂM TRA THỦ CÔNG ⚠️ (Độ tin cậy chưa đủ an toàn)"
    else:
        ket_luan = "KHÔNG ĐƯỢC SỬ DỤNG ❌ (Không xác định)"

    print("\n" + "="*50)
    print(" KẾT QUẢ PHÂN LOẠI TRÁI CÂY")
    print("="*50)
    print(f"Ảnh đầu vào: {os.path.basename(img_path)}")
    print(f"-> Loại trái cây: {loai_qua.upper()}")
    print(f"-> Trạng thái   : {do_chin.upper()}")
    print(f"-> Độ tin cậy   : {confidence:.2f}%")
    print(f"-> KẾT LUẬN     : {ket_luan}")
    print("-" * 50)
    print("Xác suất chi tiết (Mức độ chín):")
    
    prob_chin = 0.0
    prob_xanh = 0.0
    prob_hu_hong = 0.0
    
    for i, label in enumerate(labels):
        if "Ripe" in label and "Unripe" not in label:
            prob_chin += predictions[0][i] * 100
        elif "Unripe" in label:
            prob_xanh += predictions[0][i] * 100
        elif "Rotten" in label:
            prob_hu_hong += predictions[0][i] * 100
            
    print(f"  Chín        : {prob_chin:>6.2f}%")
    print(f"  Xanh        : {prob_xanh:>6.2f}%")
    print(f"  Hư hỏng     : {prob_hu_hong:>6.2f}%")
    print("="*40 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Cú pháp: python predict.py <đường_dẫn_ảnh>")
    else:
        predict_image(sys.argv[1])
