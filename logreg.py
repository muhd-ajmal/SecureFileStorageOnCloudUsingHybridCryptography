from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from sqlite3 import *
from re import *
from random import randint
from smtplib import *
from Crypto.Hash import MD5
from app import Ui_MainWindow
import sys

class Ui_MainWindow2(object):
    
    def change2reg(self):
        self.frame.setVisible(False)
        self.frame2.setVisible(True)
        self.frame3.setVisible(False)

    def change2log(self):
        self.frame.setVisible(True)
        self.frame2.setVisible(False)
        self.frame3.setVisible(False)

    def change2reset(self, event):
        self.frame.setVisible(False)
        self.frame2.setVisible(False)
        self.frame3.setVisible(True)

    checkEmail = (lambda self, email: match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    checkPassword = (lambda self, pswd: match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*])(?=.*[0-9])(?=.{8,})', pswd))
    
    def alertbox(self, icon, text, title):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def login(self):
        user = self.uname1.text().lower()
        psd = self.pswd1.text()
        try:
            if self.checkEmail(user) and self.checkPassword(psd):
                conn = connect('users.db')
                cursor = conn.cursor()
                psd2 = cursor.execute(f"SELECT PSWD FROM USERS WHERE UNAME='{user}'").fetchone()
                hval  = MD5.new()
                hval.update(psd.encode('utf-8'))
                hval = hval.hexdigest()
                if hval == psd2[0]:
                    print("Login Success!")
                    MainWindow.close()
                    ui2 = Ui_MainWindow()
                    ui2.setupUi(MainWindow)
                    MainWindow.show()

                else:
                    self.alertbox(QMessageBox.Warning, "Please enter a valid username or password", "Authentication Failed!")
            else:
                self.alertbox(QMessageBox.Warning, "Please enter a valid username or password", "Authentication Failed!")
        except:
            self.alertbox(QMessageBox.Warning, "Database error!", "Process Failed")
    def validate(self, rec_id):
        if self.checkEmail(rec_id):
            self.otp = randint(115667, 985685)
            try:
                server = SMTP('smtp.gmail.com', 587)
                server.starttls()
                uname, pswd = 'youremailid', 'appgeneratedpassword'
                server.login(uname, pswd)
                msg = f"Subject: OTP from SFCUHC\n\nYour OTP is {self.otp}"
                server.sendmail(uname, rec_id, msg)
                server.quit()
                return True
            except:
                return False
        else:
            self.alertbox(QMessageBox.Warning, "Please enter a valid email address!", "Invalid Email ID")
    
    def register(self):
        fname = self.fname.text()
        lname = self.lname.text()
        uname = self.uname2.text()
        votp = (int(self.votp.text()) == self.otp)
        pswd = self.pswd2.text()
        cpswd = self.pswd3.text()

        if len(fname) >= 3 and len(lname) >= 1:
            if self.checkEmail(uname):
                if votp:
                    if cpswd == pswd and self.checkPassword(pswd):
                        try:
                            hval  = MD5.new()
                            hval.update(pswd.encode('utf-8'))
                            hval = hval.hexdigest()
                            conn = connect('users.db')
                            cursor = conn.cursor()
                            cursor.execute(f"INSERT INTO USERS VALUES('{uname}', '{fname}', '{lname}', '{hval}')")
                            conn.commit()
                            self.alertbox(QMessageBox.Information, "Successfull       ", "Registration")
                            conn.close()
                            self.fname.setText("")
                            self.lname.setText("")
                            self.uname2.setText("")
                            self.votp.setText("")
                            self.pswd2.setText("")
                            self.pswd3.setText("")
                        except Exception as ex:
                            self.alertbox(QMessageBox.Warning, f"{ex}", "Registration Failed")
                            self.fname.setText("")
                            self.lname.setText("")
                            self.uname2.setText("")
                            self.votp.setText("")
                            self.pswd2.setText("")
                            self.pswd3.setText("")
                    else:
                        self.alertbox(QMessageBox.Warning, "The password must satisfy the following criteria: it should be more than 8 characters long, contain at least one digit, one uppercase letter, one lowercase letter, and one symbol.", "Invalid Password")
                else:
                    self.alertbox(QMessageBox.Warning, "Please enter a valid OTP!", "Invalid OTP")
            else:
                self.alertbox(QMessageBox.Warning, "Please enter a valid username!", "Invalid Email ID")
        else:
            self.alertbox(QMessageBox.Warning, "Please enter a valid name!", "Invalid Name")
            
    def recover_password(self):
        user = self.uname3.text()
        votp = (int(self.votp2.text()) == self.otp)
        pswd = self.pswd4.text()
        cpswd = self.pswd5.text()
        if self.checkEmail(user):
            if votp:
                if pswd == cpswd and self.checkPassword(pswd):
                    conn = connect('users.db')
                    cursor = conn.cursor()
                    hval  = MD5.new()
                    hval.update(pswd.encode('utf-8'))
                    hval = hval.hexdigest()
                    cursor.execute(f"UPDATE USERS SET PSWD='{hval}' WHERE UNAME='{user}'")
                    conn.commit()
                    self.alertbox(QMessageBox.Information, "Password reset successfull!", "Success")
                    conn.close()
                    self.uname3.setText("")
                    self.votp2.setText("")
                    self.pswd4.setText("")
                    self.pswd5.setText("")
                else:
                    self.alertbox(QMessageBox.Information, "The password must satisfy the following criteria: it should be more than 8 characters long, contain at least one digit, one uppercase letter, one lowercase letter, and one symbol.", "Invalid Password")
            else:
                self.alertbox(QMessageBox.Information, "Verify OTP to continue", "OTP Error")
        else:
            self.alertbox(QMessageBox.Information, "Please enter a valid username!", "Invalid Username")


    def setupUi(self, MainWindow):
        MainWindow.resize(821, 597)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 821, 601))
        self.label.setStyleSheet("QLabel{background:qlineargradient(spread:pad, x1:0, y1:0.556, x2:1, y2:1, stop:0 rgba(0, 129, 189, 255), stop:1 rgba(161, 202, 255, 255))}")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(160, 160, 471, 381))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.uname1 = QtWidgets.QLineEdit(self.frame)
        self.uname1.setGeometry(QtCore.QRect(20, 30, 439, 61))
        self.uname1.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 15px;font-weight:bold;border-radius: 30px;padding-left:20px;;}")
        self.uname1.setClearButtonEnabled(True)
        self.uname1.setObjectName("uname1")
        self.pswd1 = QtWidgets.QLineEdit(self.frame)
        self.pswd1.setGeometry(QtCore.QRect(20, 110, 439, 61))
        self.pswd1.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 15px;font-weight:bold;border-radius: 30px;padding-left:20px;;}")
        self.pswd1.setClearButtonEnabled(True)
        self.pswd1.setObjectName("pswd1")
        self.pswd1.setEchoMode(QLineEdit.Password)
        self.forgot = QtWidgets.QLabel(self.frame)
        self.forgot.setGeometry(QtCore.QRect(40, 190, 100, 31))
        self.forgot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.forgot.mousePressEvent = self.change2reset
        self.logbtn2 = QtWidgets.QPushButton(self.frame)
        self.logbtn2.setGeometry(QtCore.QRect(260, 240, 200, 61))
        self.logbtn2.setStyleSheet("QPushButton{background-color:rgba(0, 0, 0, 0.55);color:rgba(255,255,255,0.65);font-weight:bold;font-size:13px;border-radius:30px;}")
        self.logbtn2.setObjectName("logbtn2")
        self.regbtn = QtWidgets.QPushButton(self.centralwidget)
        self.regbtn.setGeometry(QtCore.QRect(60, 40, 151, 61))
        self.regbtn.setStyleSheet("QPushButton{background-color:rgba(0, 0, 0, 0.55);color:rgba(255,255,255,0.65);font-weight:bold;font-size:13px;border-top-left-radius:30px;border-bottom-left-radius:30px;}")
        self.regbtn.setObjectName("regbtn")
        self.logbtn = QtWidgets.QPushButton(self.centralwidget)
        self.logbtn.setGeometry(QtCore.QRect(210, 40, 151, 61))
        self.logbtn.setStyleSheet("QPushButton{background-color:rgba(0, 0, 0, 0.55);color:rgba(255,255,255,0.65);font-weight:bold;font-size:13px;border-top-right-radius:30px;border-bottom-right-radius:30px;}")
        self.logbtn.setObjectName("logbtn")
        self.frame2 = QtWidgets.QFrame(self.centralwidget)
        self.frame2.setGeometry(QtCore.QRect(80, 80, 691, 471))
        self.frame2.setStyleSheet("")
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setObjectName("frame2")
        self.fname = QtWidgets.QLineEdit(self.frame2)
        self.fname.setGeometry(QtCore.QRect(30, 40, 301, 51))
        self.fname.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.fname.setText("")
        self.fname.setClearButtonEnabled(True)
        self.fname.setObjectName("fname")
        self.uname2 = QtWidgets.QLineEdit(self.frame2)
        self.uname2.setGeometry(QtCore.QRect(30, 120, 301, 51))
        self.uname2.setStyleSheet("QLineEdit{background-color: rgba(0255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.uname2.setClearButtonEnabled(True)
        self.sotpbtn = QtWidgets.QPushButton(self.frame2)
        self.sotpbtn.setGeometry(QtCore.QRect(380, 120, 141, 51))
        self.sotpbtn.setStyleSheet("QPushButton{background-color:rgba(0,0,0,0.45);font-weight:700;color:rgba(255,255,255,0.65);border-radius:20px;}")
        self.sotpbtn.setObjectName("sotpbtn")
        self.votp = QtWidgets.QLineEdit(self.frame2)
        self.votp.setGeometry(QtCore.QRect(30, 200, 301, 51))
        self.votp.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.votp.setClearButtonEnabled(True)
        self.votpbtn = QtWidgets.QPushButton(self.frame2)
        self.votpbtn.setGeometry(QtCore.QRect(380, 200, 141, 51))
        self.votpbtn.setStyleSheet("QPushButton{background-color:rgba(0,0,0,0.45);font-weight:700;color:rgba(255,255,255,0.65);border-radius:20px;}")
        self.votpbtn.setObjectName("votpbtn")
        self.pswd3 = QtWidgets.QLineEdit(self.frame2)
        self.pswd3.setGeometry(QtCore.QRect(370, 300, 301, 51))
        self.pswd3.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.pswd3.setText("")
        self.pswd3.setClearButtonEnabled(True)
        self.pswd2 = QtWidgets.QLineEdit(self.frame2)
        self.pswd2.setGeometry(QtCore.QRect(30, 300, 301, 51))
        self.pswd2.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.pswd2.setText("")
        self.pswd2.setClearButtonEnabled(True)
        self.pswd2.setEchoMode(QLineEdit.Password)
        self.pswd3.setEchoMode(QLineEdit.Password)
        self.lname = QtWidgets.QLineEdit(self.frame2)
        self.lname.setGeometry(QtCore.QRect(370, 40, 301, 51))
        self.lname.setStyleSheet("QLineEdit{background-color: rgba(0255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.lname.setText("")
        self.lname.setClearButtonEnabled(True)
        self.lname.setObjectName("lname")
        self.regbtn3 = QtWidgets.QPushButton(self.frame2)
        self.regbtn3.setGeometry(QtCore.QRect(520, 390, 151, 61))
        self.regbtn3.setStyleSheet("QPushButton{background-color:rgba(0, 0, 0, 0.55);color:rgba(255,255,255,0.65);font-weight:bold;font-size:13px;border-radius:30px;}")
        self.frame3 = QtWidgets.QFrame(self.centralwidget)
        self.frame3.setGeometry(QtCore.QRect(70, 109, 691, 461))
        self.frame3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.uname3 = QtWidgets.QLineEdit(self.frame3)
        self.uname3.setGeometry(QtCore.QRect(40, 40, 291, 51))
        self.uname3.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.uname3.setClearButtonEnabled(True)
        self.sotpbtn2 = QtWidgets.QPushButton(self.frame3)
        self.sotpbtn2.setGeometry(QtCore.QRect(400, 40, 141, 51))
        self.sotpbtn2.setStyleSheet("QPushButton{background-color:rgba(0,0,0,0.45);font-weight:700;color:rgba(255,255,255,0.65);border-radius:20px;}")
        self.votp2 = QtWidgets.QLineEdit(self.frame3)
        self.votp2.setGeometry(QtCore.QRect(40, 140, 291, 51))
        self.votp2.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.votp2.setClearButtonEnabled(True)
        self.votpbtn2 = QtWidgets.QPushButton(self.frame3)
        self.votpbtn2.setGeometry(QtCore.QRect(400, 140, 141, 51))
        self.votpbtn2.setStyleSheet("QPushButton{background-color:rgba(0,0,0,0.45);font-weight:700;color:rgba(255,255,255,0.65);border-radius:20px;}")
        self.pswd4 = QtWidgets.QLineEdit(self.frame3)
        self.pswd4.setEchoMode(QLineEdit.Password)
        self.pswd4.setGeometry(QtCore.QRect(40, 250, 291, 51))
        self.pswd4.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.pswd4.setClearButtonEnabled(True)
        self.pswd5 = QtWidgets.QLineEdit(self.frame3)
        self.pswd5.setGeometry(QtCore.QRect(360, 250, 291, 51))
        self.pswd5.setStyleSheet("QLineEdit{background-color: rgba(255, 255, 255, 0.6);color: rgba(0, 0, 0, 0.75);font-size: 12px;font-weight:bold;border-radius: 20px;padding-left:20px;;}")
        self.pswd5.setClearButtonEnabled(True)
        self.pswd5.setEchoMode(QLineEdit.Password)
        self.resetbtn = QtWidgets.QPushButton(self.frame3)
        self.resetbtn.setGeometry(QtCore.QRect(410, 360, 241, 61))
        self.resetbtn.setStyleSheet("QPushButton{background-color:rgba(0, 0, 0, 0.55);color:rgba(255,255,255,0.65);font-weight:bold;font-size:13px;border-radius:30px;}")
        self.resetbtn.setObjectName("resetbtn")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.frame.setVisible(True)
        self.frame2.setVisible(False)
        self.frame3.setVisible(False)

        self.logbtn.clicked.connect(self.change2log)
        self.regbtn.clicked.connect(self.change2reg)
        
        self.logbtn2.clicked.connect(self.login)
        self.regbtn3.clicked.connect(self.register)
        self.sotpbtn.clicked.connect(lambda: self.validate(self.uname2.text()))
        self.sotpbtn2.clicked.connect(lambda: self.validate(self.uname3.text()))
        self.votpbtn.clicked.connect(lambda: self.alertbox(QMessageBox.Information, "Successfull          ", 'OTP Verification') if (self.otp == int(self.votp.text())) else self.alertbox(QMessageBox.Warning, "Unsuccessfull            ", 'OTP Verification'))
        self.votpbtn2.clicked.connect(lambda: self.alertbox(QMessageBox.Information, "Successfull          ", 'OTP Verification') if (self.otp == int(self.votp2.text())) else self.alertbox(QMessageBox.Warning, "Unsuccessfull            ", 'OTP Verification'))
        self.resetbtn.clicked.connect(self.recover_password)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SFSCHC"))
        self.pswd1.setPlaceholderText(_translate("MainWindow", "Password"))
        self.uname1.setPlaceholderText(_translate("MainWindow", "Username"))
        self.forgot.setText(_translate("MainWindow", "<a href=\"#\">Forgot Password</a>"))
        self.logbtn2.setText(_translate("MainWindow", "Login"))
        self.regbtn.setText(_translate("MainWindow", "Register"))
        self.logbtn.setText(_translate("MainWindow", "Login"))
        self.fname.setPlaceholderText(_translate("MainWindow", "First Name"))
        self.uname2.setPlaceholderText(_translate("MainWindow", "Email ID"))
        self.sotpbtn.setText(_translate("MainWindow", "Send OTP"))
        self.votp.setPlaceholderText(_translate("MainWindow", "Enter your OTP"))
        self.votpbtn.setText(_translate("MainWindow", "Verify"))
        self.pswd3.setPlaceholderText(_translate("MainWindow", "Confirm Password"))
        self.pswd2.setPlaceholderText(_translate("MainWindow", "Password"))
        self.lname.setPlaceholderText(_translate("MainWindow", "Last Name"))
        self.regbtn3.setText(_translate("MainWindow", "Register"))
        self.uname3.setPlaceholderText(_translate("MainWindow", "Email ID"))
        self.sotpbtn2.setText(_translate("MainWindow", "Send OTP"))
        self.votp2.setPlaceholderText(_translate("MainWindow", "Enter your OTP"))
        self.votpbtn2.setText(_translate("MainWindow", "Verify"))
        self.pswd4.setPlaceholderText(_translate("MainWindow", "Enter the new password"))
        self.pswd5.setPlaceholderText(_translate("MainWindow", "Confirm Password"))
        self.resetbtn.setText(_translate("MainWindow", "Change Password"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow2()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    
