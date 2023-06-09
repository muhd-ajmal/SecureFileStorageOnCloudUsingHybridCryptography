from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from main import *
from zipfile import ZipFile
import cloudinary
import cloudinary.uploader
import cloudinary.search
import requests
from sys import getsizeof

class Ui_MainWindow(object):

    isEncrypted = False
    isDecrypted = False
    isCloudConnected = False
    try:
        cloudinary.config(cloud_name="your cloud name", api_key="your api key", api_secret="secret key")
        isCloudConnected = True
    except Exception as ex:
        print(f"Cloud Error: {ex}")
        self.alertbox(QMessageBox.Warning, "Cloud connection failed. Make sure that you are connected to internet!", "Cloud Error")

    #Search files from cloud using cloudinary api, for more: https://cloudinary.com/documentation/search_api
    def search_from_cloud(self):
        try:
            if self.isCloudConnected == False:
                raise CloudConnectionFailed("Couldn't connect to cloud!")
            search_query = self.searchbar.text().lower()
            fsearch = cloudinary.search.Search()
            fsearch.expression(value="resource_type:raw")
            fsearch.sort_by('public_id', 'asc')
            result = fsearch.execute(option="")
            self.result_set = {_['filename']: _['secure_url'] for _ in result['resources'] if str(_['filename']).lower().startswith(search_query)}
            print(self.result_set)
            self.searchview.setRowCount(len(self.result_set))

            for i, data in enumerate(self.result_set.keys()):
                item = QtWidgets.QTableWidgetItem(data)
                font = QtGui.QFont()
                font.setPixelSize(20)
                item.setFont(font)
                self.searchview.setItem(i, 0, item)

        except Exception as ex:
            print(f"Cloud Error: {ex}")
            self.alertbox(QMessageBox.Warning, "Cloud connection failed. Make sure that you are connected to internet!", "Cloud Error")


    #download files from cloud using request library, Here we can get the downloadable link from cloudinary result_set
    def download_file(self):
        fname = self.searchview.currentItem().text()
        savefile = QFileDialog.getSaveFileName(None, 'output', f"{fname}", "Encrypted Files (*.sfenc)")[0]
        try:
            if self.isCloudConnected == False:
                raise CloudConnectionFailed("Couldn't connect to cloud!")
            res = requests.get(self.result_set[fname])
            with open(savefile, 'wb') as file:
                file.write(res.content)
            self.alertbox(QMessageBox.Information, "File downloaded", "Information")
        except Exception as ex:
            print(f"Cloud Error: {ex}")
            self.alertbox(QMessageBox.Warning, "Cloud connection failed. Make sure that you are connected to internet!", "Cloud Error")


    #uploading files to cloud using cloudinary.uploader for more: https://cloudinary.com/documentation/image_upload_api_reference
    def upload2cloud(self):

        if self.isEncrypted == False:
            self.alertbox(QMessageBox.Warning, "Please encrypt the file before uploading!!", "Uploading Error")
            return
        if getsizeof(self.encoutput) <= 10485760:
            fname = self.keyname.split("/")[-1].split(".")[0]
            try:
                response = cloudinary.uploader.upload(self.encoutput, resource_type="raw", use_filename='true', filename=fname, folder="Encrypted Files")
                if response:
                    self.alertbox(QMessageBox.Information, "File uploaded successfully!", "Information")
                else:
                    self.alertbox(QMessageBox.Warning, "File uploaded failed!", "Uploading Error")
            except Exception as ex:
                self.alertbox(QMessageBox.Warning, f"{ex}", "Uploading Error")
                print(ex)
        else:
            self.alertbox(QMessageBox.Warning, "Please upload a file less than 10MB", "Uploading Error")

    # It generates RSA public & private keys with the help pycryptodome library for more: https://www.pycryptodome.org/src/introduction
    def generate_RSA_keys(self):
        file = QFileDialog.getOpenFileName(None, 'Load Image', '', 'Image Files (*.png;*.jpg;*.jpeg)')[0]
        if file:
            try:
                private, public = key_generation(file, 'RSA')
                self.alertbox(QMessageBox.Information, "Key generated successfully!", "Information")
                savefilename = QFileDialog.getSaveFileName(None, 'Save File', 'RSA_keys.zip', "Zip File (*.zip)")[0]
                with ZipFile(savefilename, "w") as zfile:
                    zfile.writestr("private_key.png", private)
                    zfile.writestr("public_key.png", public)
            except:
                self.alertbox(QMessageBox.Warning, "Image processing error occurred, please upload another image to continue", "Processing Error")

    # It generates ECC public & private keys with the help of eciespy for more: https://ecies.org/py/
    def generate_ECC_keys(self):
        file = QFileDialog.getOpenFileName(None, 'Load Image', '', 'Image Files (*.png;*.jpg;*.jpeg)')[0]
        if file:
            try:
                private, public = key_generation(file, 'ECC')
                self.alertbox(QMessageBox.Information, "Key generated successfully!", "Information")
                savefilename = QFileDialog.getSaveFileName(None, 'Save File', 'ECC_keys.zip', "Zip File (*.zip)")[0]
                with ZipFile(savefilename, "w") as zfile:
                    zfile.writestr("private_key.png", private)
                    zfile.writestr("public_key.png", public)
            except:
                self.alertbox(QMessageBox.Warning, "Image processing error occurred, please upload another image to continue", "Processing Error")


    def alertbox(self, icon, text, title):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def change2Encryption(self):
        self.frame_2.setVisible(True)
        self.frame_3.setVisible(False)
        self.frame_4.setVisible(False)
        self.label.setStyleSheet("QLabel{background-image:url(\"Images/bgimage.jpg\")}")
        self.frame_2.raise_()
        self.hname.setText("Encryption")

    def change2Decryption(self):
        self.frame_2.setVisible(False)
        self.frame_3.setVisible(True)
        self.frame_4.setVisible(False)
        self.label.setStyleSheet("QLabel{background-image:url(\"Images/bgimage.jpg\")}")
        self.frame_3.raise_()
        self.hname.setText("Decryption")

    def change2Search(self):
        self.frame_2.setVisible(False)
        self.frame_3.setVisible(False)
        self.frame_4.setVisible(True)
        self.label.setStyleSheet("QLabel{background-image:url(\"Images/bgimage2.jpg\")}")
        self.frame_3.raise_()
        self.hname.setText("Search File")

    def uploadFile(self, types, obj, categ):
        self.check1 = 0
        self.check2 = 0

        if types == 1:
            if categ == "ENC" and self.enctype.currentIndex() == 0:
                self.alertbox(QMessageBox.Warning, "AES doesn't have any public key for its encryption!", "Processing Error")
                return
            self.filename = QFileDialog.getOpenFileName(None, 'Load Image', '', 'Image Files (*.png;*.jpg;*.jpeg)')[0]
            obj.setText(self.filename)
            self.check1 = 1


        elif types == 2:
            if categ == "DEC":
                self.keyname = QFileDialog.getOpenFileName()[0]
            elif categ == "ENC":
                self.keyname = QFileDialog.getOpenFileName(None, 'Load File', '', 'All Files (*.*)')[0]
                self.extension = self.keyname.split(".")[-1].lower()
            obj.setText(self.keyname)
            self.check2 = 1

    def SaveFile(self, types):
        if types == 1:
            try:
                if self.isDecrypted:
                    fname = ".".join(self.keyname.split("/")[-1].split(".")[0:-1])
                    if fname == "":
                        fname = self.keyname.split("/")[-1]
                    self.savefilename = QFileDialog.getSaveFileName(None, 'output', f"{fname}_decrypted.{self.extension}", "All Files (*.*)")[0]
                    ftype = ['dat', 'txt', 'csv']
                    if self.extension in ftype:
                        with open(self.savefilename, 'wt') as file:
                            file.write(self.decoutput)
                    else:
                        with open(self.savefilename, 'wb') as file:
                            file.write(self.decoutput)
                    self.filepath_3.setText("")
                    self.keypath_3.setText("")
                    self.pswd2.setText("")
                    self.isDecrypted = False
                    self.check1 = 0
                    self.check2 = 0
                else:
                    self.alertbox(QMessageBox.Warning, "Decrypt the files before save!", "Processing Error")
                    print("Encrypt the files before save!")
            except Exception as ex:
                print(ex)

        elif types == 2:
            try:
                if self.isEncrypted:
                    fname = ".".join(self.keyname.split("/")[-1].split(".")[0:-1])
                    self.savefilename = QFileDialog.getSaveFileName(None, 'output', f'{fname}_encrypted.sfenc', "Encrypted File (*.sfenc)")[0]
                    with open(self.savefilename, "wb") as file:
                        file.write(self.encoutput)
                    self.check1 = 0
                    self.check2 = 0
                    self.isEncrypted = False
                    self.filepath1.setText("")
                    self.keypath1.setText("")
                    self.pswd.setText("")
                else:
                    self.alertbox(QMessageBox.Warning, "Encrypt the files before save!", "Processing Error")
                    print("Encrypt the files before save!")
                self.check1 = 0
                self.check2 = 0
            except Exception as ex:
                print(f"Exception SaveFile: {ex}")

    def Encrypt(self):
        pswd = self.pswd.text()
        if not 8<=len(pswd)<=32:
            self.alertbox(QMessageBox.Warning, "Please enter a password of length between 8 to 32 characters!", "Password Error")
        else:
            try:
                error_set = {
                    chr(260): "AES encryption error!",
                    chr(261): "Please choose a valid RSA public key!",
                    chr(262): "Please choose a valid ECC public key!",
                    chr(258): "Processing error!",
                    chr(257): "Stego image error"
                }

                self.getenctype = self.enctype.currentIndex()
                self.isEncrypted = True
                if self.getenctype == 0:
                    self.encoutput = encryption(self.filepath1.text(), "", pswd, self.getenctype, self.extension)
                    if error_set.get(self.encoutput) != None:
                        self.isEncrypted = False
                        self.alertbox(QMessageBox.Warning, error_set.get(self.encoutput), "Processing Error")
                else:
                    self.encoutput = encryption(self.filepath1.text(), self.keypath1.text(), pswd, self.getenctype, self.extension)
                    if error_set.get(self.encoutput) != None:
                        self.isEncrypted = False
                        self.alertbox(QMessageBox.Warning, error_set.get(self.encoutput), "Processing Error")
                if self.isEncrypted:
                    self.alertbox(QMessageBox.Information, "Encryption phase completed!", "Information")
            except Exception as ex:
                print(ex)

    def Decrypt(self):
        error_set = {
            chr(258): "Invalid RSA private key!",
            chr(257): "Please enter a valid password!",
            chr(255): "Invalid ECC private key!",
            chr(259): "Processing Error!"
        }
        pswd2 = self.pswd2.text()
        if not 8<=len(pswd2)<=32 and self.check2:
            self.alertbox(QMessageBox.Warning, "Please enter a password of length between 8 to 32 characters!", "Password Error")
        else:
            try:
                self.decoutput, self.extension = decryption(self.filepath_3.text(), self.keypath_3.text(), pswd2)
                if self.decoutput in error_set.keys():
                    self.alertbox(QMessageBox.Warning, f"{error_set[self.decoutput]}", "Processing Error")
                    self.isDecrypted = False
                else:
                    self.isDecrypted = True
                    self.alertbox(QMessageBox.Information, "Decryption phase completed!", "Information")
            except Exception as ex:
                self.alertbox(QMessageBox.Warning, "Please upload a valid encrypted file", "File Error")
                print(f"Exception: {ex}")

    
    def logout(self):
        import sys
        sys.exit()
        

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(956, 719)
        MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("QWidget{\nbackground:rgba(0,0,0,0.5);\n}\nQMenuBar{\nbackground-color:rgba(0,0,0,0.65);\ncolor:white;\nfont-weight:bold;\nfont-size:18px;\n}\nQMenuBar:focus{\ncolor:black;\n}\nQMenu{\ncolor:white;\nbackground-color:rgba(0,0,0,0.65);\n}\n\nQStatusBar{\nbackground-color:rgba(0,0,0,0.65);\ncolor:white;\n}\nQPushButton{\nbackground-color:rgba(0,0,0,0.65);\ncolor:rgba(255,255,255,0.85);\noutline:none;\nborder:2px solid rgba(0,0,0,0.65);\nborder-top-left-radius:30px;\nborder-bottom-left-radius:30px;\nfont-weight:bold;\nfont-size:16px;\n}\nQPushButton:hover{\nbackground-color:rgba(255,255,255,0.85);\ncolor:rgba(0,0,0,0.65);\nborder-color:rgba(255,255,255,0.85);\n}\nQLabel{\nbackground:rgba(255,255,255,1)\n}")
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.ForceTabbedDocks|QtWidgets.QMainWindow.GroupedDragging|QtWidgets.QMainWindow.VerticalTabs)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(30, 120, 871, 521))
        self.frame_2.setStyleSheet("QFrame{\nbackground:none;\n}")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.browsebtn1 = QtWidgets.QPushButton(self.frame_2)
        self.browsebtn1.setGeometry(QtCore.QRect(40, 40, 131, 61))
        self.browsebtn1.setStyleSheet("")
        self.browsebtn1.setObjectName("browsebtn1")
        self.browsebtn2 = QtWidgets.QPushButton(self.frame_2)
        self.browsebtn2.setGeometry(QtCore.QRect(40, 250, 131, 61))
        self.browsebtn2.setStyleSheet("")
        self.browsebtn2.setObjectName("browsebtn2")
        self.filepath1 = QtWidgets.QLabel(self.frame_2)
        self.filepath1.setGeometry(QtCore.QRect(170, 40, 361, 61))
        self.filepath1.setStyleSheet("QLabel{background-color:none;font-size:14px;\npadding-left:10px;\nborder:2px solid rgba(0,0,0,0.65);\nborder-left:none;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.filepath1.setText("")
        self.filepath1.setObjectName("filepath1")
        self.keypath1 = QtWidgets.QLabel(self.frame_2)
        self.keypath1.setGeometry(QtCore.QRect(170, 250, 361, 61))
        self.keypath1.setStyleSheet("QLabel{\nbackground-color:none;\nfont-size:14px;padding-left:10px;\nborder:2px solid rgba(0,0,0,0.65);\nborder-left:none;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.keypath1.setText("")
        self.keypath1.setObjectName("keypath1")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(60, 10, 491, 21))
        self.label_3.setStyleSheet("QLabel{\nfont-weight:bold;\nfont-size:15px;\nbackground-color:rgba(0,0,0,0.0)\n}")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(60, 220, 491, 21))
        self.label_4.setStyleSheet("QLabel{\nfont-weight:bold;\nfont-size:15px;\nbackground-color:rgba(0,0,0,0.0)\n}")
        self.label_4.setObjectName("label_4")
        self.uploadbtn = QtWidgets.QPushButton(self.frame_2)
        self.uploadbtn.setGeometry(QtCore.QRect(370, 430, 161, 61))
        self.uploadbtn.setStyleSheet("QPushButton{\nborder-radius:0px;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.uploadbtn.setObjectName("uploadbtn")

        self.genkeybtn = QtWidgets.QPushButton(self.frame_2)
        self.genkeybtn.setGeometry(QtCore.QRect(610, 350, 241, 61))
        self.genkeybtn.setStyleSheet("QPushButton{\nborder-radius:30px;\n}")
        self.genkeybtn.setObjectName("genkeybtn")

        self.genkeybtn_2 = QtWidgets.QPushButton(self.frame_2)
        self.genkeybtn_2.setGeometry(QtCore.QRect(610, 430, 241, 61))
        self.genkeybtn_2.setStyleSheet("QPushButton{\nborder-radius:30px;\n}")
        self.genkeybtn_2.setObjectName("genkeybtn_2")

        self.savefilebtn1 = QtWidgets.QPushButton(self.frame_2)
        self.savefilebtn1.setGeometry(QtCore.QRect(40,430, 161, 61))
        self.savefilebtn1.setObjectName("savefilebtn1")

        self.encryptbtn = QtWidgets.QPushButton(self.frame_2)
        self.encryptbtn.setGeometry(QtCore.QRect(200, 430, 171, 61))
        self.encryptbtn.setStyleSheet("QPushButton{\nborder-radius:0px;\n}")
        self.encryptbtn.setObjectName("encryptbtn")

        self.pswd = QtWidgets.QLineEdit(self.frame_2)
        self.pswd.setGeometry(QtCore.QRect(40, 340, 491, 61))
        self.pswd.setStyleSheet("QLineEdit{background-color:rgba(255,255,255,0.5);border:2px solid rgba(0,0,0,0.65);border-radius:30px;padding-right:15px;padding-left:15px;font-weight:bold;font-size:15px;}")
        self.pswd.setInputMask("")
        self.pswd.setText("")
        self.pswd.setEchoMode(QLineEdit.Password)
        self.pswd.setClearButtonEnabled(True)
        self.pswd.setObjectName("pswd")
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setGeometry(QtCore.QRect(50, 120, 491, 21))
        self.label_5.setStyleSheet("QLabel{font-weight:bold;font-size:15px;background-color:rgba(0,0,0,0.0)}")
        self.label_5.setObjectName("label_5")
        self.enctype = QtWidgets.QComboBox(self.frame_2)
        self.enctype.setGeometry(QtCore.QRect(50, 150, 471, 51))
        self.enctype.setStyleSheet("QComboBox{background-color:rgba(255,255,255,0.5); border:2px solid rgba(0,0,0,0.65); border-radius:30px; padding-left:15px;padding-right:15px;font-weight:bold;font-size:15px;}")
        self.enctype.setObjectName("enctype")
        for _ in range(3):
            self.enctype.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(0, 0, 961, 681))
        self.label.setStyleSheet("QLabel{\nbackground-image:url(\"Images/bgimage.jpg\");background-size:cover;background-repeat:none;\n}")
        self.label.setText("")
        self.label.setObjectName("label")
        self.hname = QtWidgets.QLabel(self.centralwidget)
        self.hname.setGeometry(QtCore.QRect(0, -8, 971, 91))
        self.hname.setStyleSheet("QLabel{\nfont-weight:bold;\nfont-size:35px;\nbackground-color:rgba(0,0,0,0.65);color:rgba(255,255,255,0.3);\n}")
        self.hname.setAlignment(QtCore.Qt.AlignCenter)
        self.hname.setObjectName("hname")
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setGeometry(QtCore.QRect(60, 120, 571, 461))
        self.frame_3.setStyleSheet("QFrame{\nbackground:none;\n}")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.browsebtn3 = QtWidgets.QPushButton(self.frame_3)
        self.browsebtn3.setGeometry(QtCore.QRect(30, 70, 131, 61))
        self.browsebtn3.setStyleSheet("")
        self.browsebtn3.setObjectName("browsebtn3")
        self.browsebtn4 = QtWidgets.QPushButton(self.frame_3)
        self.browsebtn4.setGeometry(QtCore.QRect(30, 200, 131, 61))
        self.browsebtn4.setStyleSheet("")

        self.browsebtn4.setObjectName("browsebtn4")
        self.filepath_3 = QtWidgets.QLabel(self.frame_3)
        self.filepath_3.setGeometry(QtCore.QRect(160, 70, 361, 61))
        self.filepath_3.setStyleSheet("QLabel{\nbackground-color:none;\nfont-size:14px;\nword-wrap:break;\npadding-left:10px;\nborder:2px solid rgba(0,0,0,0.65);\nborder-left:none;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.filepath_3.setText("")
        self.filepath_3.setObjectName("filepath_3")
        self.keypath_3 = QtWidgets.QLabel(self.frame_3)
        self.keypath_3.setGeometry(QtCore.QRect(160, 200, 361, 61))
        self.keypath_3.setStyleSheet("QLabel{\nbackground-color:none;\nfont-size:14px;\nword-wrap:break;\npadding-left:10px;\nborder:2px solid rgba(0,0,0,0.65);\nborder-left:none;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.keypath_3.setText("")
        self.keypath_3.setObjectName("keypath_3")
        self.label_7 = QtWidgets.QLabel(self.frame_3)
        self.label_7.setGeometry(QtCore.QRect(50, 40, 491, 21))
        self.label_7.setStyleSheet("QLabel{\nfont-weight:bold;\nfont-size:15px;\nbackground-color:rgba(0,0,0,0.0)\n}")
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.frame_3)
        self.label_8.setGeometry(QtCore.QRect(50, 170, 491, 21))
        self.label_8.setStyleSheet("QLabel{\nfont-weight:bold;\nfont-size:15px;\nbackground-color:rgba(0,0,0,0.0)\n}")
        self.label_8.setObjectName("label_8")

        self.pswd2 = QtWidgets.QLineEdit(self.frame_3)
        self.pswd2.setGeometry(QtCore.QRect(30, 300, 491, 61))
        self.pswd2.setStyleSheet("QLineEdit{background-color:rgba(255,255,255,0.5);border:2px solid rgba(0,0,0,0.65);border-radius:30px;padding-right:15px;padding-left:15px;font-weight:bold;font-size:15px;}")
        self.pswd2.setInputMask("")
        self.pswd2.setText("")
        self.pswd2.setEchoMode(QLineEdit.Password)
        self.pswd2.setClearButtonEnabled(True)
        self.pswd2.setObjectName("pswd2")

        self.decryptbtn = QtWidgets.QPushButton(self.frame_3)
        self.decryptbtn.setGeometry(QtCore.QRect(270, 390, 161, 61))
        self.decryptbtn.setStyleSheet("QPushButton{\nborder-radius:0px;\nborder-top-right-radius:30px;\nborder-bottom-right-radius:30px;\n}")
        self.decryptbtn.setObjectName("decryptbtn")
        self.savefilebtn2 = QtWidgets.QPushButton(self.frame_3)
        self.savefilebtn2.setGeometry(QtCore.QRect(120, 390, 151, 61))
        self.savefilebtn2.setObjectName("savefilebtn2")
        self.label.raise_()

        self.frame_4 = QtWidgets.QFrame(self.centralwidget)
        self.frame_4.setGeometry(QtCore.QRect(40, 80, 851, 551))
        self.frame_4.setStyleSheet("QFrame{background:none;}")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.searchbtn = QtWidgets.QPushButton(self.frame_4)
        self.searchbtn.setGeometry(QtCore.QRect(510, 50, 131, 61))
        self.searchbtn.setStyleSheet(
            "QPushButton{border-radius:none;border-top-right-radius:30px;border-bottom-right-radius:30px;}QPushButton:hover{border-color:rgba(0,0,0,0.65);border-left:none;}")
        self.searchbtn.setObjectName("searchbtn")
        self.searchbar = QtWidgets.QLineEdit(self.frame_4)
        self.searchbar.setGeometry(QtCore.QRect(170, 50, 341, 61))
        self.searchbar.setStyleSheet(
            "QLineEdit{background-color:none;font-size:15px;font-weight:600;padding-left:15px;border:2px solid rgba(0,0,0,0.65);border-right:none;border-top-left-radius:30px;border-bottom-left-radius:30px;}")
        self.searchbar.setObjectName("searchbar")
        self.searchview = QtWidgets.QTableWidget(self.frame_4)
        self.searchview.setGeometry(QtCore.QRect(40, 141, 761, 381))
        self.searchview.setStyleSheet("QTableView{border:2px solid rgba(0,0,0,0.65);background-color:rgba(255,255,255,0.35);font-size:15px;}")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(300)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.searchview.sizePolicy().hasHeightForWidth())
        self.searchview.setSizePolicy(sizePolicy)
        self.searchview.setObjectName("searchview")
        self.searchview.setColumnCount(1)
        self.searchview.setColumnWidth(0, 760)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(18)
        item.setFont(font)
        self.searchview.setHorizontalHeaderItem(0, item)
        self.searchview.verticalHeader().setVisible(False)

        self.frame_4.setVisible(False)

        self.frame_2.raise_()
        self.hname.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 956, 31))
        self.menubar.setObjectName("menubar")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLogin = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionLogin.setFont(font)
        self.actionDecryption = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionDecryption.setFont(font)
        self.actionSearch_File = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionSearch_File.setFont(font)

        self.actionLogout = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionLogout.setFont(font)

        self.menuTools.addAction(self.actionLogin)
        self.menuTools.addAction(self.actionDecryption)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionSearch_File)
        self.menuTools.addAction(self.actionLogout)
        self.menubar.addAction(self.menuTools.menuAction())

        self.actionLogin.triggered.connect(self.change2Encryption)
        self.actionDecryption.triggered.connect(self.change2Decryption)
        self.actionSearch_File.triggered.connect(self.change2Search)
        self.actionLogout.triggered.connect(self.logout)

        self.browsebtn1.clicked.connect(lambda: self.uploadFile(2, self.filepath1, "ENC"))
        self.browsebtn2.clicked.connect(lambda: self.uploadFile(1, self.keypath1, "ENC"))
        self.browsebtn3.clicked.connect(lambda: self.uploadFile(2, self.filepath_3, "DEC"))
        self.browsebtn4.clicked.connect(lambda: self.uploadFile(1, self.keypath_3, "DEC"))
        self.encryptbtn.clicked.connect(self.Encrypt)
        self.decryptbtn.clicked.connect(self.Decrypt)
        self.savefilebtn1.clicked.connect(lambda: self.SaveFile(2))
        self.savefilebtn2.clicked.connect(lambda: self.SaveFile(1))
        self.uploadbtn.clicked.connect(self.upload2cloud)
        self.genkeybtn.clicked.connect(self.generate_RSA_keys)
        self.genkeybtn_2.clicked.connect(self.generate_ECC_keys)
        self.searchbtn.clicked.connect(self.search_from_cloud)
        self.searchview.clicked.connect(self.download_file)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SFSCUHC"))
        MainWindow.setMaximumSize(953, 719)
        MainWindow.setMinimumSize(953, 719)
        self.browsebtn1.setText(_translate("MainWindow", "Browse"))
        self.pswd.setPlaceholderText(_translate("MainWindow", "Enter the password"))
        self.pswd2.setPlaceholderText(_translate("MainWindow", "Enter the password"))
        self.genkeybtn.setText(_translate("MainWindow", "Generate RSA Keys"))
        self.genkeybtn_2.setText(_translate("MainWindow", "Generate ECC Keys"))
        self.browsebtn2.setText(_translate("MainWindow", "Browse"))
        self.label_3.setText(_translate("MainWindow", "Upload File"))
        self.label_4.setText(_translate("MainWindow", "Upload Image (Public key image)"))
        self.uploadbtn.setText(_translate("MainWindow", "Upload File"))
        self.savefilebtn1.setText(_translate("MainWindow", "Save File"))
        self.encryptbtn.setText(_translate("MainWindow", "Encrypt"))
        self.hname.setText(_translate("MainWindow", "Encryption"))
        self.browsebtn3.setText(_translate("MainWindow", "Browse"))
        self.label_5.setText(_translate("MainWindow", "Select Encryption Type"))
        self.enctype.setItemText(0, _translate("MainWindow", "AES"))
        self.enctype.setItemText(1, _translate("MainWindow", "AES + RSA"))
        self.enctype.setItemText(2, _translate("MainWindow", "ECC + BlowFish + MD5"))
        self.browsebtn4.setText(_translate("MainWindow", "Browse"))
        self.label_7.setText(_translate("MainWindow", "Upload File"))
        self.label_8.setText(_translate("MainWindow", "Upload Image (Stego Key)"))
        self.decryptbtn.setText(_translate("MainWindow", "Decrypt"))
        self.savefilebtn2.setText(_translate("MainWindow", "Save File"))
        self.menuTools.setTitle(_translate("MainWindow", "Options"))
        self.actionLogin.setText(_translate("MainWindow", "Encryption"))
        self.actionDecryption.setText(_translate("MainWindow", "Decryption"))
        self.actionSearch_File.setText(_translate("MainWindow", "Search File"))
        self.actionLogout.setText(_translate("MainWindow", "Logout"))
        self.searchbtn.setText(_translate("MainWindow", "Search"))
        self.searchbar.setPlaceholderText(_translate("MainWindow", "Search by file name"))
        item = self.searchview.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "File Name"))