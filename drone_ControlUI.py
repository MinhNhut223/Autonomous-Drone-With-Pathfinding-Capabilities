from PyQt5 import QtCore, QtGui, QtWidgets, Qt
import serial
import sys 
import keyboard

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.serial_connected = False
        try:
            self.serial = serial.Serial('COM5', 115200, timeout=1)  # Adjust 'COM3' to your actual COM port
            self.serial_connected = True
        except serial.SerialException as e:
            self.show_error_message(str(e))
            
        self.arm_timer = QtCore.QTimer()  # Khởi tạo arm_timer ở đây
        self.arm_timer.timeout.connect(self.reset_controls)

        self.button_timers = {}  # Lưu trữ timer cho từng nút
        self.is_sending_commands = {}  # Lưu trữ trạng thái gửi lệnh cho từng nút
        self.button_commands = {  # Dictionary để lưu trữ lệnh điều khiển
            self.pushButton_1: "1700,1500,1500,1500\n",  # Tiến lên
            self.pushButton_2: "1500,1700,1500,1500\n",  # Qua phải
            self.pushButton_3: "1500,1300,1500,1500\n",  # Qua trái
            self.pushButton_4: "1300,1500,1500,1500\n",  # Lùi lại
            self.pushButton_5: "1500,1500,1500,1300\n",  # Xoay trái
            self.pushButton_6: "1500,1500,1700,1500\n",  # Nâng lên
            self.pushButton_7: "1500,1500,1300,1500\n",  # Hạ xuống
            self.pushButton_8: "1500,1500,1500,1700\n",  # Xoay phải
        }
        for button in self.button_commands.keys():
            self.is_sending_commands[button] = False
            button.pressed.connect(lambda b=button: self.start_sending_command(b))
            button.released.connect(lambda b=button: self.stop_sending_command(b))

        # Khởi tạo giá trị mặc định cho các trục
        self.roll = 1500
        self.pitch = 1500
        self.throttle = 1500
        self.yaw = 1500
        self.is_armed = False
        
        # Tạo timer để gửi lệnh liên tục
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.send_current_command)
        self.timer.start(50)  # Gửi lệnh mỗi 100ms / 10Hz

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1062, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Khởi tạo các nút nhấn
        self.pushButton_1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_1.setGeometry(QtCore.QRect(740, 140, 150, 70))
        self.pushButton_1.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(840, 230, 150, 70))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(640, 230, 150, 70))
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(740, 320, 150, 70))
        self.pushButton_4.setObjectName("pushButton_4")

        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(40, 230, 150, 70))
        self.pushButton_5.setObjectName("pushButton_5")

        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(170, 150, 150, 70))
        self.pushButton_6.setObjectName("pushButton_6")

        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(170, 320, 150, 70))
        self.pushButton_7.setObjectName("pushButton_7")

        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_8.setGeometry(QtCore.QRect(280, 230, 150, 70))
        self.pushButton_8.setObjectName("pushButton_8")

        # Dictionary để lưu trữ lệnh điều khiển

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)

        # Kết nối các nút bấm với hàm xử lý
        # self.pushButton_1.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_1))
        # self.pushButton_2.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_2))
        # self.pushButton_3.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_3))
        # self.pushButton_4.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_4))
        # self.pushButton_5.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_5))
        # self.pushButton_6.clicked.connect(lambda: self.handle_button_press(self.pushButton_6))
        # self.pushButton_7.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_7))
        # self.pushButton_8.clicked.connect(lambda checked=False: self.handle_button_press(self.pushButton_8))  # Bỏ qua tham số checked

        # Thêm nút nhấn "Arm/Disarm"
        self.armButton = QtWidgets.QPushButton(self.centralwidget)
        self.armButton.setGeometry(QtCore.QRect(450, 70, 101, 61))  # Vị trí tùy chỉnh
        self.armButton.setObjectName("armButton")
        self.armButton.setText("Arm/Disarm")

        self.armButton.clicked.connect(self.arm_drone)

        # Thêm QLabel để hiển thị trạng thái arm
        self.armLabel = QtWidgets.QLabel(self.centralwidget)
        self.armLabel.setGeometry(QtCore.QRect(450, 90, 101, 61))  # Vị trí tùy chỉnh
        self.armLabel.setObjectName("armLabel")
        self.armLabel.setText("Disarmed")
        self.armButton.setStyleSheet("background-color: red")  # Đặt màu đỏ khi Disarmed
        self.armLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.menubar.setGeometry(QtCore.QRect(0, 0, 583, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_1.setText(_translate("MainWindow", "Tiến lên"))
        self.pushButton_2.setText(_translate("MainWindow", "Qua bên phải"))
        self.pushButton_3.setText(_translate("MainWindow", "Qua bên trái"))
        self.pushButton_4.setText(_translate("MainWindow", "Lùi lại"))
        self.pushButton_5.setText(_translate("MainWindow", "Xoay tròn qua trái"))
        self.pushButton_6.setText(_translate("MainWindow", "Nâng lên"))
        self.pushButton_7.setText(_translate("MainWindow", "Hạ xuống"))
        self.pushButton_8.setText(_translate("MainWindow", "Xoay tròn qua phải"))

    def show_error_message(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def arm_drone(self):
        if self.is_armed == True:
            self.roll = 1050
            self.pitch = 1050
            self.throttle = 1050
            self.yaw = 1950
            self.is_armed = False
            self.send_current_command()
            self.arm_timer.start(1500)
            self.armLabel.setText("Disarmed")
            self.armButton.setStyleSheet("background-color: red")  # Đặt màu đỏ khi Disarmed
            QtCore.QTimer.singleShot(1500, self.update_disarm_label)

        else:
            self.roll = 1050
            self.pitch = 1050
            self.throttle = 1050
            self.yaw = 1950
            self.is_armed = True
            self.send_current_command()
            self.arm_timer.start(1500)
            self.armLabel.setText("Armed")
            self.armButton.setStyleSheet("background-color: green")  # Đặt màu xanh khi Armed


            # Tạo timer để hiển thị trạng thái "Armed" sau 1.5 giây
            QtCore.QTimer.singleShot(1500, self.update_arm_label)

    def update_arm_label(self):
        self.armLabel.setText("Armed")  # Cập nhật trạng thái arm hiển thị lên giao diện

    def update_disarm_label(self):
        self.armLabel.setText("Disarmed")  # Cập nhật trạng thái disarmed hiển thị lên giao diện

    def reset_controls(self):
        self.roll = 1500
        self.pitch = 1500
        self.throttle = 1500
        self.yaw = 1500
        self.send_current_command()
        self.arm_timer.stop()

    def start_sending_command(self, button):
        self.is_sending_commands[button] = True
        self.button_timers[button] = QtCore.QTimer()
        self.button_timers[button].timeout.connect(lambda: self.gui_lenh(button))
        self.button_timers[button].start(5)  

    def stop_sending_command(self, button):
        self.is_sending_commands[button] = False
        self.button_timers[button].stop()
        self.reset_controls()

    def gui_lenh(self, button=None):
        if button:  # Nếu có nút được nhấn giữ
            command_str = self.button_commands.get(button)
            if command_str and self.serial_connected and self.is_sending_commands[button]:
                try:
                    self.serial.write(command_str.encode())
                    print(f"Sent command: {command_str}")
                except serial.SerialException as e:
                    self.show_error_message(str(e))
        else:  # Nếu không có nút nào được nhấn giữ, gửi lệnh mặc định
            self.send_command(self.roll, self.pitch, self.throttle, self.yaw)

    def send_command(self, roll, pitch, throttle, yaw):
        command = f"{roll},{pitch},{throttle},{yaw}\n"
        if self.serial_connected:
            try:
                self.serial.write(command.encode())
                print(f"Sent command: {command}")
            except serial.SerialException as e:
                self.show_error_message(str(e))
                print(f"Failed to send command: {command}")
        else:
            self.show_error_message("Serial connection not established.")
            print(f"Failed to send command (serial not connected): {command}")

    def send_current_command(self):
        self.send_command(self.roll, self.pitch, self.throttle, self.yaw)

    def handle_button_press(self, command, button):
        self.send_command(command)
        self.flash_button(button)
    
    def keyPressEvent(self, event):
        key = event.key()
        if keyboard.is_pressed('w'):
            self.throttle = 1700
        if keyboard.is_pressed('s'):
            self.throttle = 1300
        if keyboard.is_pressed('a'):
            self.yaw = 1300
        if keyboard.is_pressed('d'):
            self.yaw = 1700
            self.yaw = min(2000, self.yaw)  # Giới hạn yaw
        if keyboard.is_pressed('i'):
            self.pitch = 1700
            self.pitch = min(2000, self.pitch)
        if keyboard.is_pressed('k'):
            self.pitch = 1300
            self.pitch = max(1000, self.pitch)
        if keyboard.is_pressed('l'):
            self.roll = 1700
            self.roll = min(2000, self.roll)
        if keyboard.is_pressed('j'):
            self.roll = 1300
            self.roll = max(1000, self.roll)

    def keyReleaseEvent(self, event):
        # Trả các trục về giá trị trung tính khi nhả phím
        self.roll = 1500
        self.pitch = 1500
        self.throttle = 1500
        self.yaw = 1500

    def flash_button(self, button):
        original_color = button.palette().color(QtGui.QPalette.Button)
        button.setStyleSheet("background-color: yellow")
        QtCore.QTimer.singleShot(200, lambda: button.setStyleSheet(f"background-color: {original_color.name()}"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())