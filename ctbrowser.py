"""
pyuic5 'ctbrowser.ui' -o ctbrowser_ui.py
"""
path = r"C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\backtothefuture\separation_highlighted\High Cycle\CT Scans_0.3 ml Treated_T032_D2_Degen_00002351_00004080_D0004121.ISQ;1.png"
root = r"C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\backtothefuture\separation_highlighted\High Cycle"

import sys, os, itk, numpy as np, cv2 as cv, pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QGridLayout, QListWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage

#from ctbrowser_ui import Ui_MainWindow

from pathlookup import pathlookup
import bttf_utilities as bu
from bttf_utilities import beautify_and_resize as br
from bttf_constants import text_params
from plotting import get_line as gl, stitch

class Window(QMainWindow):
    def __init__(self, root=None):
        super().__init__()
        uic.loadUi('ctbrowser.ui',self)
        #self.setupUi(self)
        
        #Populate list widget with all files in folder.
        self.root = root
        self.files = bu.find(root, ".png")
        self.list.addItems([file.split("\\")[-1] for file in self.files])
        
        #Set central widget to be the gridLayoutWidget so that our grid expands to fill QMainWindow
        self.setCentralWidget(self.gridLayoutWidget)
        
        #Load a pixmap into the viewport.
        pixmap = QPixmap(path)
        self.viewport.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        
        #Move window to a comfortable position.
        self.move(100,100)
        
        #Set default axis along which to view slices.
        self.axis = 2
        
        #DataFrame to store observations
        self.df = pd.read_csv('output_data.csv', keep_default_na=False)
    

    def preview(self):
        #Get zeroth item in selection.
        item = self.list.selectedItems()[0]
        #print("previewing ", item.text())
        
        #Get filepath of selcted image by joining current folder to image name, and construct a QPixmap from it.
        pixmap = QPixmap(os.path.join(root, item.text()))
        
        #Display the QPixmap and resize the window to fit.
        self.viewport.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        
        #Find the current sample's info row in the DataFrame and load that info into the GUI fields
        current_row = self.df.loc[self.df['sample'] == item.text()]
        self.comment.setText(current_row['comment'].values[0])
        self.valid.setChecked(bool(current_row['valid'].values[0]))
        
            
    def load(self, item):
        #Delete previous image3d to free up memory.
        if "image3d" in self.__dict__:
            del self.image3d; del self.image3d_h; print("Deleted image3d")
        
        #Check if path is the filepath of an actual CT, or the name of a preview image that we have to look up.
        if os.path.exists(item.text()):
            isq_path = item.text()
        else:
            isq_path = pathlookup[item.text()]
        
        #Read image from disk and store it as a HashableArray.
        print('reading from disk...')
        imageio = itk.ScancoImageIO.New()
        self.image3d = np.asarray(itk.imread(isq_path, imageio=imageio)).view(bu.HashableNDArray)
        
        #Generate MPS plot and highlight gap.
        self.plot = gl(bu.get_max_per_slice(self.image3d))
        self.image3d_h, self.gap_width = bu.highlight_gap(self.image3d.copy(), tolerate_upto = 1.3)
        
        #Enable the slider and set its maximum value to the number of slices along the current axis. Enable checkbox.
        self.slider.setEnabled(True)
        self.slider.setMaximum(self.image3d.shape[self.axis]-1)
        self.highlight.setEnabled(True)
        
        #Indicate CT path in window title.
        self.setWindowTitle(isq_path)
        print("loaded ",isq_path)
    
    def slide(self, position):
        #Construct a slice tuple based on the current axis, and get that slice.
        slicer = (slice(None),)*self.axis+(position,)
        ctslice = self.image3d_h[slicer] if self.highlight.isChecked() else self.image3d[slicer]
        
        #Beautify&resize the image.
        image = br(ctslice, 0.75) #some resize factors cause misdrawing of pixmap
        
        # Find min/maxes
        min_pixel = image.min()
        max_pixel = image.max()
        
        #Attach the generated MPS plot and overlay info text.
        image = stitch(image, self.plot)
        cv.putText(img = image, text = f'min:{min_pixel}, max:{max_pixel}, gap width: {self.gap_width if "gap_width" in self.__dict__ else ""}', **text_params)
        
        #Convert the image to a QImage, then to a QPixmap.
        qim = QImage(image, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap(qim)
        
        #Display the QPixmap and resize the window to fit.
        self.viewport.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height()) #FIXME when switching from axis 0 to 1, window height remains the same
        
    def nextclicked(self):
        self.axis = (self.axis + 1)%3
        self.axis_label.setText(str(self.axis))
        
        self.slider.setMaximum(self.image3d.shape[self.axis]-1)
        self.slide(self.slider.maximum()//2)
        
    def prevclicked(self):
        self.axis = (self.axis - 1)%3
        self.axis_label.setText(str(self.axis))
        
        self.slider.setMaximum(self.image3d.shape[self.axis]-1)
        self.slide(self.slider.maximum()//2)
    
    def highlight_checkbox_changed(self,*args):
        self.slide(self.slider.sliderPosition())
        
    def saveclicked(self):
        print("save")
        samplename = self.list.selectedItems()[0].text()
        
        self.df.loc[self.df['sample'] == samplename, 'comment'] = self.comment.text()
        self.df.loc[self.df['sample'] == samplename, 'valid'] = int(bool(self.valid.checkState()))
        
        pass

    def closeEvent(self, event):
        self.df.to_csv('output_data.csv', index=False)
        print('Saved data to output_data.csv.')
        
        
if __name__ =='__main__':
    app = QApplication(sys.argv)
    win = Window(root)
    win.show()
    sys.exit(app.exec())
pass
