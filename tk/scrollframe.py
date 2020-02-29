from tkinter import *
from tkinter.ttk import *


class DoubleScrollbarFrame( Frame):

  def __init__(self, master, **kwargs):
    '''
      Initialisation. The DoubleScrollbarFrame consist of :
        - an horizontal scrollbar
        - a  vertical   scrollbar
        - a canvas in which the user can place sub-elements
    '''

    Frame.__init__(self,  master, **kwargs)

    # Canvas creation with double scrollbar
    self.hscrollbar =  Scrollbar(self, orient = HORIZONTAL)
    self.vscrollbar =  Scrollbar(self, orient = VERTICAL)
    self.sizegrip =  Sizegrip(self)
    self.canvas = Canvas(self, bd=0, highlightthickness=0, 
                                  yscrollcommand = self.vscrollbar.set,
                                  xscrollcommand = self.hscrollbar.set)
    self.vscrollbar.config(command = self.canvas.yview)
    self.hscrollbar.config(command = self.canvas.xview)

  def pack(self, **kwargs):
    '''
      Pack the scrollbar and canvas correctly in order to recreate the same look as MFC's windows. 
    '''

    self.hscrollbar.pack(side = BOTTOM, fill=X, expand=FALSE)
    self.vscrollbar.pack(side = RIGHT, fill=Y,  expand=FALSE)
    self.sizegrip.pack(in_ = self.hscrollbar, side = BOTTOM, anchor = "se")
    self.canvas.pack(side=LEFT, padx=5, pady=5,
                                             fill=BOTH, expand=TRUE)
    Frame.pack(self, **kwargs)
    


  def get_frame(self):
    '''
      Return the "frame" useful to place inner controls.
    '''
    return self.canvas


if __name__ == '__main__':

    # Top-level frame
    root = Tk()
    root.title( "Double scrollbar with tkinter" )
    root.minsize(width = 600, height = 600)
    frame = DoubleScrollbarFrame(root, relief="sunken")

    # Add controls here
    #subframe =  Frame( frame.get_frame() ) 
    #txt =  Label(subframe, text="Add things here !")
    for i in range(50):
      Label(master=frame.get_frame(), text=str(i)).pack(side=TOP, fill=X, expand=0)

  #Packing everything
    #txt.pack(anchor = 'center', fill = Y, expand = Y)
    #subframe.pack(padx = 15, pady = 15, fill = BOTH, expand = TRUE)
    frame.pack( padx = 5, pady = 5, expand = True, fill = BOTH)


  # launch the GUI
    root.mainloop()