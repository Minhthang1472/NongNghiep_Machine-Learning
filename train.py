import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.applications import MobileNetV2 # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout # type: ignore
from tensorflow.keras.models import Model # type: ignore
import matplotlib.pyplot as plt

# --- CÁC THÔNG SỐ CƠ BẢN ---
IMG_SIZE = (224, 224) # Kích thước chuẩn cho MobileNetV2
BATCH_SIZE = 32       # Số lượng ảnh học mỗi lần
EPOCHS = 15           # Số vòng lặp huấn luyện (tăng lên nếu muốn mô hình khôn hơn)
NUM_CLASSES = 4       # Số lượng nhãn (chín, xanh, chín vừa, hư hỏng)

TRAIN_DIR = 'dataset/train'

def build_model(num_classes):
    print(f"[INFO] Đang khởi tạo mô hình MobileNetV2 cho {num_classes} loại trái cây...")
    # Tải mô hình MobileNetV2 (bỏ phần phân loại ở trên cùng đi)
    base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    
    # Đóng băng các lớp của mô hình cơ sở
    base_model.trainable = False

    # Thêm các lớp phân loại của riêng chúng ta
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x) # Giảm overfitting
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Biên dịch mô hình
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    # 1. Đọc dữ liệu (có chức năng xoay, lật ảnh để tăng đa dạng)
    print("[INFO] Đang chuẩn bị dữ liệu hình ảnh...")
    datagen = ImageDataGenerator(
        rescale=1./255, 
        rotation_range=20,
        horizontal_flip=True,
        validation_split=0.2 # Dành 20% dữ liệu để tự kiểm tra
    )

    # Đọc dữ liệu Train
    train_generator = datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    # Đọc dữ liệu Validation
    val_generator = datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    # Kiểm tra xem có ảnh không
    if train_generator.samples == 0:
        print("\n[LỖI] Không tìm thấy ảnh nào! Hãy đảm bảo bạn đã chép ảnh vào các thư mục: dataset/train/chin, dataset/train/xanh, ...")
        return

    # Lưu tên các nhãn ra file txt
    labels = train_generator.class_indices
    labels = dict((v,k) for k,v in labels.items())
    with open('labels.txt', 'w', encoding='utf-8') as f:
        for v in labels.values():
            f.write(f"{v}\n")
    print(f"[INFO] Đã nhận diện các nhãn: {labels}")

    # 2. Xây dựng mô hình
    num_classes = train_generator.num_classes
    model = build_model(num_classes)

    # 3. Tiến hành huấn luyện
    print("[INFO] Bắt đầu quá trình huấn luyện (Training)...")
    history = model.fit(train_generator, epochs=EPOCHS, validation_data=val_generator)

    # 4. Lưu lại trí thông minh (Model)
    model.save('fruit_model.h5')
    print("\n[INFO] Đã lưu mô hình thành công vào file 'fruit_model.h5'.")

    # 5. Vẽ biểu đồ để báo cáo
    # Biểu đồ Accuracy
    plt.plot(history.history['accuracy'], label='Độ chính xác (Train)')
    plt.plot(history.history['val_accuracy'], label='Độ chính xác (Validation)')
    plt.title('Biểu đồ Độ Chính Xác')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('accuracy_plot.png')
    plt.close()

    # Biểu đồ Loss
    plt.plot(history.history['loss'], label='Mức độ lỗi (Train)')
    plt.plot(history.history['val_loss'], label='Mức độ lỗi (Validation)')
    plt.title('Biểu đồ Mức Độ Lỗi')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig('loss_plot.png')
    plt.close()
    
    print("[INFO] Đã lưu biểu đồ ra file 'accuracy_plot.png' và 'loss_plot.png'.")

if __name__ == '__main__':
    main()
