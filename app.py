import sys
import os
import numpy as np
import tensorflow as tf
from keras.preprocessing import image
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                               QFrame, QProgressBar, QGridLayout)
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon, QColor
from PySide6.QtCore import Qt

# Tắt cảnh báo TF
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

IMG_SIZE = (224, 224)

# Giao diện Đen - Cam (Dark/Orange Theme) giống hệt ảnh mẫu
QSS = """
QMainWindow {
    background-color: #121212;
}
QLabel {
    color: #E0E0E0;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel#TitleLabel {
    color: #FF9800;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 2px;
}
QLabel#SectionTitle {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#DataLabel {
    color: #888888;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#DataValue {
    color: #FF9800;
    font-size: 15px;
    font-weight: bold;
}
QLabel#StatusValue {
    font-size: 14px;
    font-weight: bold;
}
QPushButton#UploadBtn {
    background-color: #FF9800;
    color: #000000;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 4px;
    padding: 15px;
    letter-spacing: 1px;
}
QPushButton#UploadBtn:hover {
    background-color: #FFA726;
}
QPushButton#UploadBtn:pressed {
    background-color: #F57C00;
}
QProgressBar {
    background-color: #2C2C2C;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: right;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #FF9800;
    border-radius: 3px;
}
QFrame#AnalysisFrame, QFrame#ImageFrame {
    background-color: #1A1A1A;
    border-radius: 8px;
    border: 1px solid #2A2A2A;
}
"""

class FruitScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FRUIT_SCANNER_V1.0")
        self.setGeometry(100, 100, 850, 600)
        self.setStyleSheet(QSS)
        
        # Load Model
        self.model = None
        self.labels = []
        self.load_model_data()

        self.init_ui()

    def load_model_data(self):
        model_path = 'fruit_model.h5'
        label_path = 'labels.txt'
        try:
            self.model = tf.keras.models.load_model(model_path)
            with open(label_path, 'r', encoding='utf-8') as f:
                self.labels = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Lỗi tải model: {e}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)
        
        # ==========================================
        # CỘT TRÁI: HÌNH ẢNH VÀ NÚT TẢI LÊN
        # ==========================================
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        title_lbl = QLabel("🍊 FRUIT_SCANNER_V1.0")
        title_lbl.setObjectName("TitleLabel")
        left_layout.addWidget(title_lbl)
        
        img_frame = QFrame()
        img_frame.setObjectName("ImageFrame")
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_img_title = QLabel("SELECTED FRUIT")
        lbl_img_title.setObjectName("DataLabel")
        
        self.img_display = QLabel()
        self.img_display.setAlignment(Qt.AlignCenter)
        self.img_display.setFixedSize(380, 380)
        self.img_display.setStyleSheet("background-color: #0F0F0F; border-radius: 6px;")
        
        img_layout.addWidget(lbl_img_title)
        img_layout.addWidget(self.img_display)
        left_layout.addWidget(img_frame)
        
        btn_upload = QPushButton("⇧ UPLOAD_IMAGE")
        btn_upload.setObjectName("UploadBtn")
        btn_upload.clicked.connect(self.select_image)
        left_layout.addWidget(btn_upload)
        
        main_layout.addLayout(left_layout)
        
        # ==========================================
        # CỘT PHẢI: BẢNG ĐIỀU KHIỂN & KẾT QUẢ
        # ==========================================
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 45, 0, 0) # Căn lùi xuống một chút cho cân với title bên trái
        
        analysis_frame = QFrame()
        analysis_frame.setObjectName("AnalysisFrame")
        a_layout = QVBoxLayout(analysis_frame)
        a_layout.setSpacing(20)
        a_layout.setContentsMargins(25, 25, 25, 25)
        
        # Tiêu đề phân tích
        a_title = QLabel("REAL-TIME ANALYSIS")
        a_title.setObjectName("SectionTitle")
        a_layout.addWidget(a_title)
        
        # Grid chứa thông tin Loại quả và Trạng thái
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        
        lbl_type_title = QLabel("FRUIT TYPE")
        lbl_type_title.setObjectName("DataLabel")
        self.lbl_type_val = QLabel("---")
        self.lbl_type_val.setObjectName("DataValue")
        self.lbl_type_val.setAlignment(Qt.AlignRight)
        
        lbl_status_title = QLabel("STATUS")
        lbl_status_title.setObjectName("DataLabel")
        self.lbl_status_val = QLabel("---")
        self.lbl_status_val.setObjectName("StatusValue")
        self.lbl_status_val.setAlignment(Qt.AlignRight)
        self.lbl_status_val.setStyleSheet("color: #555555;") # Màu xám mặc định
        
        grid.addWidget(lbl_type_title, 0, 0)
        grid.addWidget(self.lbl_type_val, 0, 1)
        grid.addWidget(lbl_status_title, 1, 0)
        grid.addWidget(self.lbl_status_val, 1, 1)
        
        a_layout.addLayout(grid)
        
        # Confidence Score & Progress Bar
        conf_layout = QHBoxLayout()
        lbl_conf_title = QLabel("CONFIDENCE SCORE")
        lbl_conf_title.setObjectName("DataLabel")
        self.lbl_conf_val = QLabel("0.0%")
        self.lbl_conf_val.setObjectName("DataValue")
        self.lbl_conf_val.setAlignment(Qt.AlignRight)
        conf_layout.addWidget(lbl_conf_title)
        conf_layout.addWidget(self.lbl_conf_val)
        
        a_layout.addLayout(conf_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        a_layout.addWidget(self.progress_bar)
        
        # Phân cách (Đường kẻ ngang)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("border: 1px solid #333333;")
        a_layout.addWidget(line)
        
        # QA Recommendation (Lời khuyên tự động)
        qa_title = QLabel("QA RECOMMENDATION")
        qa_title.setObjectName("SectionTitle")
        a_layout.addWidget(qa_title)
        
        self.lbl_qa_val = QLabel("SYS.READY\nWaiting for image input...")
        self.lbl_qa_val.setWordWrap(True)
        self.lbl_qa_val.setStyleSheet("color: #AAAAAA; font-size: 14px; line-height: 1.5; padding-top: 10px;")
        self.lbl_qa_val.setAlignment(Qt.AlignTop)
        a_layout.addWidget(self.lbl_qa_val, 1) # stretch=1
        
        right_layout.addWidget(analysis_frame)
        main_layout.addLayout(right_layout)
        
        if self.model is None:
            self.lbl_qa_val.setText("ERROR: Model components missing. Cannot start AI engine.")
            self.lbl_qa_val.setStyleSheet("color: #F44336; font-weight: bold;")

    def select_image(self):
        if self.model is None: return
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Thu nhỏ ảnh vừa khung đen
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_display.setPixmap(pixmap)
            self.predict(file_path)

    def predict(self, img_path):
        self.lbl_qa_val.setText("PROCESSING // RUNNING NEURAL NET...")
        self.lbl_qa_val.setStyleSheet("color: #FF9800; font-size: 14px; font-weight: bold;")
        QApplication.processEvents()
        
        try:
            img = image.load_img(img_path, target_size=IMG_SIZE)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0
            
            predictions = self.model.predict(img_array)
            best_idx = np.argmax(predictions[0])
            confidence = predictions[0][best_idx] * 100
            predicted_label = self.labels[best_idx]
            
            loai_qua = "Unknown"
            do_chin = "Unknown"
            
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
            
            # QA Logic & Colors
            if do_chin == "Hư hỏng":
                ket_luan = f"REJECTED ❌\n{loai_qua} đã hỏng, yêu cầu loại bỏ ngay."
                color = "#F44336" # Đỏ rực
                status_dot = "● ROTTEN"
            elif do_chin == "Xanh":
                if loai_qua == "Chuối":
                    ket_luan = "WARNING ⚠️\nChuối còn xanh, cần ủ thêm 2-3 ngày."
                elif loai_qua == "Cam":
                    ket_luan = "WARNING ⚠️\nCam còn xanh, vắt nước sẽ rất chua."
                elif loai_qua == "Ổi":
                    ket_luan = "WARNING ⚠️\nỔi xanh, thịt cứng và chát."
                elif loai_qua == "Táo":
                    ket_luan = "WARNING ⚠️\nTáo xanh, độ đường chưa đạt chuẩn."
                elif loai_qua == "Dâu Tây":
                    ket_luan = "WARNING ⚠️\nDâu tây chưa chín, vị chua gắt."
                else:
                    ket_luan = f"WARNING ⚠️\n{loai_qua} còn xanh, chưa đạt tiêu chuẩn."
                color = "#FFC107" # Vàng cam
                status_dot = "● UNRIPE"
            elif do_chin == "Chín":
                if confidence >= 75.0:
                    if loai_qua == "Chuối":
                        ket_luan = "APPROVED ✅\nChuối chín vàng, tối ưu để dùng tươi."
                    elif loai_qua == "Cam":
                        ket_luan = "APPROVED ✅\nCam mọng nước, vitamin C cao nhất."
                    elif loai_qua == "Nho":
                        ket_luan = "APPROVED ✅\nNho chín ngọt, thích hợp ép rượu."
                    elif loai_qua == "Lựu":
                        ket_luan = "APPROVED ✅\nLựu chín đỏ, đạt chuẩn thu hoạch."
                    elif loai_qua == "Dâu Tây":
                        ket_luan = "APPROVED ✅\nDâu tây chín mọng, cần bảo quản lạnh."
                    elif loai_qua == "Táo":
                        ket_luan = "APPROVED ✅\nTáo thơm, giòn ngọt, đạt chuẩn xuất khẩu."
                    else:
                        ket_luan = f"APPROVED ✅\n{loai_qua} chín đẹp, đạt chuẩn an toàn."
                    color = "#4CAF50" # Xanh lá
                    status_dot = "● RIPE_OPTIMAL"
                else:
                    ket_luan = "MANUAL CHECK ⚠️\nĐộ tin cậy hệ thống dưới ngưỡng an toàn."
                    color = "#FFC107"
                    status_dot = "● RIPE_LOW_CONF"
            else:
                ket_luan = "UNKNOWN ❌"
                color = "#F44336"
                status_dot = "● ERROR"
                
            # Cập nhật thông số
            self.lbl_type_val.setText(f"{loai_qua.upper()}")
            
            # Cập nhật màu Status
            self.lbl_status_val.setText(status_dot)
            self.lbl_status_val.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            
            # Cập nhật Confidence Bar
            self.lbl_conf_val.setText(f"{confidence:.1f}%")
            self.progress_bar.setValue(int(confidence))
            
            # Cập nhật Lời khuyên QA
            self.lbl_qa_val.setText(ket_luan)
            self.lbl_qa_val.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; line-height: 1.5; padding-top: 10px;")
            
        except Exception as e:
            self.lbl_qa_val.setText(f"SYS_ERROR:\n{e}")
            self.lbl_qa_val.setStyleSheet("color: #F44336;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FruitScannerApp()
    window.show()
    sys.exit(app.exec())
