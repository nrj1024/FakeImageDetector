import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QSystemTrayIcon, QFileDialog, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSlider
from PyQt5.QtGui import QCursor, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
import ctypes
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from PIL.ImageQt import ImageQt
import PIL.ExifTags
import cv2 as cv
from matplotlib import pyplot as plt
from NeuralNets import initClassifier, initSegmenter

class FID:
   def __init__(self):
      self.win=QWidget()
      self.win.setFixedSize(640,480)
      self.win.setWindowTitle("Fake Image Detector")
      self.l=QLabel(self.win)
      self.l.setGeometry(0,462,640,18)
      self.l.setText('  Ready!')

   def splashScreen(self):
      img = QLabel(self.win)
      img.setGeometry(0,0,640,480)
      pixmap = QPixmap('SplashScreen.png')
      img.setPixmap(pixmap.scaled(640,480,Qt.KeepAspectRatio))
      QTimer.singleShot(3000, img.hide)

   def mainScreen(self):
      newanalysis_bt=QPushButton(self.win)
      newanalysis_bt.setText('New Analysis')
      newanalysis_bt.move(225,190)
      newanalysis_bt.setCursor(QCursor(Qt.PointingHandCursor))
      newanalysis_bt.clicked.connect(self.newanalysis)

      newhist_bt=QPushButton(self.win)
      newhist_bt.setText('View History')
      newhist_bt.move(225,240)
      newhist_bt.setCursor(QCursor(Qt.PointingHandCursor))
      #newhist_bt.clicked.connect(self.dummyhist)

   def ovrd_dragEnterEvent(self, event):
      if event.mimeData().hasImage:
         event.accept()
      else:
         event.ignore()
   
   def ovrd_dropEvent(self, event):
      self.file_path = event.mimeData().urls()[0].toLocalFile()
      print(self.file_path)
      self.imageWindow()

   def newanalysis(self):
      self.newanalysis_win=QWidget()
      self.newanalysis_win.move(320,125)
      self.newanalysis_win.setFixedSize(640,480)
      self.newanalysis_win.setWindowTitle("New Analysis")

      self.dragndrop=QLabel('Drag and Drop here', self.newanalysis_win)
      self.dragndrop.move(225,170)
      self.dragndrop.setStyleSheet("border :3px solid black; border-style : dashed")
      self.dragndrop.resize(200,80)
      self.dragndrop.setAlignment(Qt.AlignCenter)
      self.dragndrop.setAcceptDrops(True)

      self.dragndrop.dragEnterEvent = self.ovrd_dragEnterEvent.__get__(self.dragndrop,QLabel)
      self.dragndrop.dropEvent = self.ovrd_dropEvent.__get__(self.dragndrop,QLabel)
      
      browse_bt=QPushButton(self.newanalysis_win)
      browse_bt.setText('Browse')
      browse_bt.move(225,280)
      browse_bt.setCursor(QCursor(Qt.PointingHandCursor))
      browse_bt.clicked.connect(self.browsefile)
      self.newanalysis_win.show()

   def browsefile(self):
      self.fileloc = QFileDialog.getOpenFileName(self.newanalysis_win,"Select an Image file",filter="Image File (*.jpg *.png)")
      if self.fileloc[0]=='':
         self.l.setText('  File not chosen!')
      else:
         self.file_path=self.fileloc[0]
         self.imageWindow()

   def imageWindow(self):
      self.imageWindow_win=QWidget()
      self.imageWindow_win.move(320,125)
      self.imageWindow_win.setFixedSize(640,480)
      self.imageWindow_win.setWindowTitle("Image")
      
      self.imagelabel = QLabel(self.imageWindow_win)
      self.imagelabel.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))

      image_bt=QPushButton(self.imageWindow_win)
      image_bt.setText('Get Metadata')
      image_bt.move(395,165)
      image_bt.setCursor(QCursor(Qt.PointingHandCursor))
      image_bt.clicked.connect(self.metadata)

      image_bt2=QPushButton(self.imageWindow_win)
      image_bt2.setText('Run Analysis')
      image_bt2.move(395,215)
      image_bt2.setCursor(QCursor(Qt.PointingHandCursor))
      image_bt2.clicked.connect(self.runAnalysis)

      image_bt3=QPushButton(self.imageWindow_win)
      image_bt3.setText('Manual Tools')
      image_bt3.move(395,265)
      image_bt3.setCursor(QCursor(Qt.PointingHandCursor))
      image_bt3.clicked.connect(self.manualtools)

      
      self.imageWindow_win.show()

   def metadata(self):
      self.metadata_win=QWidget()
      self.metadata_win.move(320,125)
      self.metadata_win.setFixedSize(640,480)
      self.metadata_win.setWindowTitle("Metadata")

      img = PIL.Image.open(self.file_path)
      exif={}

      for k, v in img._getexif().items():
         if k in PIL.ExifTags.TAGS:
            exif[PIL.ExifTags.TAGS[k]]=v

      metadata_str=''
      for k,v in exif.items():
         metadata_str+=str(k)+' : '+str(v)+' \n\n'

      data = QTextEdit(self.metadata_win)
      data.move(20,20)
      data.resize(600,440)
      data.setText(metadata_str)

      self.metadata_win.show()

   def runAnalysis(self):
      self.runAnalysis_win=QWidget()
      self.runAnalysis_win.move(320,125)
      self.runAnalysis_win.setFixedSize(640,480)
      self.runAnalysis_win.setWindowTitle("AI Analysis")

      self.model=initClassifier()
      self.model.load_weights('classifier_weights.h5')
      testimg=self.convert_to_ela_image(self.file_path, 90).resize((256,256))
      test=np.array(testimg)/255
      test=test.reshape(-1,256,256,3)
      result=self.model.predict(test)
      print('Chances of being real : ',round(result[0][0],3))
      print('Chances of being fake : ',round(result[0][1],3))

      self.imagelabel1 = QLabel(self.runAnalysis_win)
      self.imagelabel1.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel1.setPixmap(pixmap.scaled(300,300))

      self.restitle=QLabel(self.runAnalysis_win)
      if result[0][0]>=0.5:
         self.restitle.setText('REAL')
      else:
         self.restitle.setText('FAKE')
      self.restitle.setStyleSheet('color: white; background-color: #e76f51; font-size:30px;')
      self.restitle.setGeometry(425,95,145,60)
      self.restitle.setAlignment(Qt.AlignCenter)

      self.percreal=QLabel(self.runAnalysis_win)
      self.percreal.setText(str(round(result[0][0]*100,3))+'% real')
      self.percreal.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.percreal.setGeometry(400,150,190,40)
      self.percreal.setAlignment(Qt.AlignCenter)

      self.percfake=QLabel(self.runAnalysis_win)
      self.percfake.setText(str(round(result[0][1]*100,3))+'% fake')
      self.percfake.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.percfake.setGeometry(400,180,190,40)
      self.percfake.setAlignment(Qt.AlignCenter)

      img = PIL.Image.open(self.file_path)
      exif={}

      for k, v in img._getexif().items():
         if k in PIL.ExifTags.TAGS:
            exif[PIL.ExifTags.TAGS[k]]=v
      self.lastus=QLabel(self.runAnalysis_win)
      self.lastus.setText('Last Used Software : \n'+str(exif['Software']))
      self.lastus.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.lastus.setGeometry(370,250,250,80)
      self.lastus.setAlignment(Qt.AlignCenter)


      genMask_bt=QPushButton(self.runAnalysis_win)
      genMask_bt.setText('Generate Mask')
      genMask_bt.move(395,345)
      genMask_bt.setCursor(QCursor(Qt.PointingHandCursor))
      genMask_bt.clicked.connect(self.genMask)

      self.runAnalysis_win.show()

   def genMask(self):
      self.model=initSegmenter()
      self.model.load_weights('segmenter_weights.h5')
      testimg=self.convert_to_ela_image(self.file_path,90).resize((256,256))
      testimg=testimg.getchannel('B')
      test=np.array(testimg)/np.max(testimg)
      test=test.reshape(-1,256,256,1)
      result=self.model.predict(test)
      result=result.reshape(256,256)
      result=(result*255).astype('uint8')
      plt.figure('Binary Mask')
      plt.imshow(result, cmap='gray')
      plt.show()

   def manualtools(self):
      self.manualtools_win=QWidget()
      self.manualtools_win.move(320,125)
      self.manualtools_win.setFixedSize(640,480)
      self.manualtools_win.setWindowTitle("Manual Tools")

      mtools_bt1=QPushButton(self.manualtools_win)
      mtools_bt1.setText('Error Level Analysis')
      mtools_bt1.move(225,140)
      mtools_bt1.setCursor(QCursor(Qt.PointingHandCursor))
      mtools_bt1.clicked.connect(self.ErrorLA)

      mtools_bt2=QPushButton(self.manualtools_win)
      mtools_bt2.setText('Luminous Gradient')
      mtools_bt2.move(225,190)
      mtools_bt2.setCursor(QCursor(Qt.PointingHandCursor))
      mtools_bt2.clicked.connect(lambda:self.luminance_gradient(self.file_path))

      mtools_bt3=QPushButton(self.manualtools_win)
      mtools_bt3.setText('Noise Map')
      mtools_bt3.move(225,240)
      mtools_bt3.setCursor(QCursor(Qt.PointingHandCursor))
      mtools_bt3.clicked.connect(self.noisemap)

      mtools_bt4=QPushButton(self.manualtools_win)
      mtools_bt4.setText('Edge Map')
      mtools_bt4.move(225,290)
      mtools_bt4.setCursor(QCursor(Qt.PointingHandCursor))
      mtools_bt4.clicked.connect(lambda:self.detect_edges(self.file_path))

      self.manualtools_win.show()

   def ErrorLA(self):
      self.ela_win=QWidget()
      self.ela_win.move(320,125)
      self.ela_win.setFixedSize(640,480)
      self.ela_win.setWindowTitle("Error Level Analysis")

      self.imagelabel = QLabel(self.ela_win)
      self.imagelabel.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))

      self.int=QLabel('Intensity',self.ela_win)
      self.int.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.int.setGeometry(450,150,100,40)
      self.int.setAlignment(Qt.AlignCenter)

      self.sl = QSlider(self.ela_win)
      self.sl.setRange(0,100)
      self.sl.setOrientation(Qt.Horizontal)
      self.sl.setGeometry(400,200,200,20)

      apply_bt=QPushButton(self.ela_win)
      apply_bt.setText('Apply')
      apply_bt.move(400,250)
      apply_bt.setCursor(QCursor(Qt.PointingHandCursor))
      apply_bt.clicked.connect(lambda:self.show_ela(self.file_path))
      
      self.ela_win.show()

   def luminousgradient(self):
      self.luminousgradient_win=QWidget()
      self.luminousgradient_win.move(320,125)
      self.luminousgradient_win.setFixedSize(640,480)
      self.luminousgradient_win.setWindowTitle("Luminous Gradient")

      self.imagelabel = QLabel(self.luminousgradient_win)
      self.imagelabel.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))

      self.int=QLabel('Intensity',self.luminousgradient_win)
      self.int.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.int.setGeometry(450,150,100,40)
      self.int.setAlignment(Qt.AlignCenter)

      self.sl = QSlider(self.luminousgradient_win)
      self.sl.setRange(0,100)
      self.sl.setOrientation(Qt.Horizontal)
      self.sl.setGeometry(400,200,200,20)

      apply_bt=QPushButton(self.luminousgradient_win)
      apply_bt.setText('Apply')
      apply_bt.move(400,250)
      apply_bt.setCursor(QCursor(Qt.PointingHandCursor))
      #apply_bt.clicked.connect()

      self.luminousgradient_win.show()


   def noisemap(self):
      self.noisemap_win=QWidget()
      self.noisemap_win.move(320,125)
      self.noisemap_win.setFixedSize(640,480)
      self.noisemap_win.setWindowTitle("Noise Map")

      self.imagelabel = QLabel(self.noisemap_win)
      self.imagelabel.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))

      self.int=QLabel('Intensity',self.noisemap_win)
      self.int.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.int.setGeometry(450,150,100,40)
      self.int.setAlignment(Qt.AlignCenter)

      self.sl = QSlider(self.noisemap_win)
      self.sl.setRange(0,100)
      self.sl.setOrientation(Qt.Horizontal)
      self.sl.setGeometry(400,200,200,20)

      apply_bt=QPushButton(self.noisemap_win)
      apply_bt.setText('Apply')
      apply_bt.move(400,250)
      apply_bt.setCursor(QCursor(Qt.PointingHandCursor))
      apply_bt.clicked.connect(lambda:self.apply_na(self.file_path))

      self.noisemap_win.show()

   def edgemap(self):
      self.edgemap_win=QWidget()
      self.edgemap_win.move(320,125)
      self.edgemap_win.setFixedSize(640,480)
      self.edgemap_win.setWindowTitle("Edge Map")

      self.imagelabel = QLabel(self.edgemap_win)
      self.imagelabel.setGeometry(50,90,300,300)
      pixmap = QPixmap(self.file_path)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))

      self.int=QLabel('Intensity',self.edgemap_win)
      self.int.setStyleSheet('color: white; background-color: #e76f51; font-size:16px;')
      self.int.setGeometry(450,150,100,40)
      self.int.setAlignment(Qt.AlignCenter)

      self.sl = QSlider(self.edgemap_win)
      self.sl.setRange(0,100)
      self.sl.setOrientation(Qt.Horizontal)
      self.sl.setGeometry(400,200,200,20)

      apply_bt=QPushButton(self.edgemap_win)
      apply_bt.setText('Apply')
      apply_bt.move(400,250)
      apply_bt.setCursor(QCursor(Qt.PointingHandCursor))
      #apply_bt.clicked.connect()

      self.edgemap_win.show()

   def convert_to_ela_image(self, path, quality,intensity=None):
      filename = path
      resaved_filename = 'tempresaved.jpg'
      ELA_filename = 'tempela.png'
      
      im = Image.open(filename).convert('RGB')
      im.save(resaved_filename, 'JPEG', quality = quality)
      resaved_im = Image.open(resaved_filename)
      
      ela_im = ImageChops.difference(im, resaved_im)
      
      extrema = ela_im.getextrema()
      max_diff = max([ex[1] for ex in extrema])
      if max_diff == 0:
         max_diff = 1
      scale = 255.0 / max_diff
      if intensity==None:
         ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
      else:
         ela_im = ImageEnhance.Brightness(ela_im).enhance(intensity)
      return  ela_im
      
   def show_ela(self, path):
      intensity=self.sl.value()
      ela_im=self.convert_to_ela_image(self.file_path, 90, intensity)
      qim = ImageQt(ela_im)
      pixmap = QPixmap.fromImage(qim)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))
      self.imagelabel.update()

   def detect_edges(self, path):
      image = Image.open(path)   
      image = image.convert("L") #Converting to greyscale
      image = image.filter(ImageFilter.FIND_EDGES)
      image = np.array(image.resize((300,300)))
      plt.figure('Edge Map')
      plt.imshow(image, cmap='gray', aspect='equal')
      plt.show()

   def luminance_gradient(self, path):
      img = cv.imread(path,0)
      laplacian = cv.Laplacian(img,cv.CV_64F)
      sobelx = cv.Sobel(img,cv.CV_64F,1,0,ksize=15)
      image = Image.fromarray(sobelx).resize((300,300))
      plt.figure('Luminance Gradient')
      plt.imshow(np.array(image), cmap='gray', aspect='equal')
      plt.show()

   def noise_analysis(self, path, quality, intensity):
      filename = path
      resaved_filename = 'tempresaved.jpg'
      
      im = Image.open(filename).convert('L')
      im.save(resaved_filename, 'JPEG', quality = quality)
      resaved_im = Image.open(resaved_filename)
      
      na_im = ImageChops.difference(im, resaved_im)
      
      extrema = na_im.getextrema()
      max_diff = max([ex for ex in extrema])
      if max_diff == 0:
         max_diff = 1
      scale = (255.0 / max_diff)
      
      na_im = ImageEnhance.Brightness(na_im).enhance(intensity)
      
      return na_im

   def apply_na(self, path):
      intensity=self.sl.value()
      na=self.noise_analysis(self.file_path, 90, intensity)
      qim = ImageQt(na)
      pixmap = QPixmap.fromImage(qim)
      self.imagelabel.setPixmap(pixmap.scaled(300,300))
      self.imagelabel.update()

   def run(self):
      self.mainScreen()
      self.splashScreen()
      self.win.show()
      sys.exit(app.exec_())


if __name__ == '__main__':
   #myappid = 'G05.fakeimagedetector'
   #ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
   app = QApplication([])
   app.setStyleSheet(open('StyleSheet.css').read())
   app.setWindowIcon(QIcon('icon.png'))
   instance=FID()
   instance.run()
