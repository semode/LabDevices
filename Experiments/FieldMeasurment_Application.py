
"""

"""

from enthought.traits.api import HasTraits, Str, Instance, Array, Button, Any, Enum, Int, Event,Trait, Callable, NO_COMPARE
from enthought.traits.ui.api import View, VGroup, HGroup, Item, Controller, Group, Tabbed
from enthought.enable.api import BaseTool
from enthought.traits.api import on_trait_change
from enthought.traits.ui.editors import ButtonEditor
from enthought.chaco.default_colormaps import *
from enthought.traits.ui.menu import Action, CloseAction, Menu, MenuBar, OKCancelButtons, Separator
                 
from enthought.chaco.api import ArrayDataSource, ArrayPlotData, ColorBar, ContourLinePlot, \
                                 ColormappedScatterPlot, CMapImagePlot, \
                                 ContourPolyPlot, DataRange1D, VPlotContainer, \
                                 DataRange2D, GridMapper, GridDataSource, \
                                 HPlotContainer, ImageData, LinearMapper, \
                                 LinePlot, OverlayPlotContainer, Plot, PlotAxis, ImageData
                                 
from enthought.enable.api import Window                     
                         
from enthought.enable.api import ComponentEditor, Component

from threading import Thread
from Devices.TranslationalStage_3Axes import TranslationalStage_3Axes
from Devices.Thorlabs_PM100D import Thorlabs_PM100D
from matplotlib import rc
from time import sleep

from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator

from numpy import array, linspace, meshgrid, nanmin, nanmax,  pi, zeros, ones, save, load, \
                append, hstack, vstack
from enthought.chaco.tools.api import LineInspector, PanTool, RangeSelection, \
                                   RangeSelectionOverlay, ZoomTool, DragZoom
                                   
from enthought.traits.api import File
from enthought.traits.ui.key_bindings import KeyBinding, KeyBindings
from pylab import unravel_index



class FieldData(HasTraits):
    """ Data and Index of the field
    """  
    __slots__ = 'intens_xy','intens_yz', 'intens_xz'
    intens_yz = Array(comparison_mode=NO_COMPARE)
    intens_xy = Array(comparison_mode=NO_COMPARE)
    intens_xz = Array(comparison_mode=NO_COMPARE)
    
class CaptureThread(Thread):

    def run(self):
        self.measure4()
    def measure4(self): 
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        to_limit_speed = 2
        self.fd.intens_xy=array([[]])
        stage.AG_UC2_1.set_step_amplitude(1, self.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(1, -self.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(2, self.step_amplitude_backwards)
        stage.AG_UC2_1.set_step_amplitude(2, -self.step_amplitude_backwards)
        stage.AG_UC2_2.set_step_amplitude(1, self.step_amplitude_up)
        stage.AG_UC2_2.set_step_amplitude(1, -self.step_amplitude_up)        
        stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
        stage.AG_UC2_1.move_to_limit(2, -to_limit_speed)
        stage.AG_UC2_1.print_step_amplitudes()
        stage.AG_UC2_2.print_step_amplitudes()
        
        # acquire plane in yz-plane
        self.fd.intens_yz = zeros((self.steps_backwards, self.steps_side))
        for i in range(0,self.steps_backwards):
            for j in range(0,self.steps_side):
                if self.wants_abort:
                    return
                self.fd.intens_yz[i,j] = power_meter.getPower()
                stage.left(self.steps_per_move)  
            stage.backwards(self.steps_per_move)
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
            self.fd.intens_yz = self.fd.intens_yz # this is to update the array for a traits callback
        #acquire vertical plane   
        stage.AG_UC2_1.move_to_limit(2,-to_limit_speed)
        max_index=unravel_index(self.fd.intens_yz.argmax(), self.fd.intens_yz.shape) # find index of the max intensity
        stage.left(max_index[1])
        stage.AG_UC2_2.move_to_limit(1,-to_limit_speed) 
        
        self.fd.intens_xz = zeros((self.steps_backwards, self.steps_up))
        for i in range(0,self.steps_backwards):
            for j in range(0,self.steps_up):
                if self.wants_abort:
                    return
                self.fd.intens_xz[i,j] = power_meter.getPower()
                stage.up(self.steps_per_move)
            stage.backwards(self.steps_per_move)
            stage.AG_UC2_2.move_to_limit(1, -to_limit_speed)
            self.fd.intens_xz = self.fd.intens_xz
                  
    def measure3(self):
        try:
            power_meter  = Thorlabs_PM100D("PM100D")
            stage       = TranslationalStage_3Axes('COM3','COM4')   
        except:
            print "Exception raised: Devices not available"
            return
        to_limit_speed = 2
        self.fd.intens_xy=array([[]])
        stage.AG_UC2_1.set_step_amplitude(1, self.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(1, -self.step_amplitude_side)
        stage.AG_UC2_1.set_step_amplitude(2, self.step_amplitude_backwards)
        stage.AG_UC2_1.set_step_amplitude(2, -self.step_amplitude_backwards)
        stage.AG_UC2_2.set_step_amplitude(1, self.step_amplitude_up)
        stage.AG_UC2_2.set_step_amplitude(1, -self.step_amplitude_up)        
        stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
        stage.AG_UC2_1.move_to_limit(2, -to_limit_speed)
        stage.AG_UC2_1.print_step_amplitudes()
        stage.AG_UC2_2.print_step_amplitudes()

        for i in range(0,self.steps_backwards):
            row=array([])
            for j in range(0,self.steps_side):
                if self.wants_abort:
                    return
                row = append(power_meter.getPower(),row)
                stage.left(self.steps_per_move)
            if i==0:
                self.fd.intens_xy = append(self.fd.intens_xy, row)
            else:
                self.fd.intens_xy = vstack((self.fd.intens_xy, row))    
            stage.backwards(self.steps_per_move)
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
            
        #acquire vertical plane   
        stage.AG_UC2_1.move_to_limit(2,-to_limit_speed)
        max_index=unravel_index(self.fd.intens_xy.argmax(), self.fd.intens_xy.shape)
        stage.backwards(max_index[0])
        stage.AG_UC2_2.move_to_limit(1,-to_limit_speed) # check for direction
        self.fd.intens_xy = array([[]])
        
        for i in range(0,self.steps_up):
            row=array([])
            for j in range(0,self.steps_side):
                if self.wants_abort:
                    return
                row = append(power_meter.getPower(),row)
                stage.left(self.steps_per_move)
            if i==0:
               self.fd.intens_xy = append(self.fd.intens_xy, row)
            else:
                self.fd.intens_xy = vstack((self.fd.intens_xy, row))    
            stage.up(self.steps_per_move)
            stage.AG_UC2_1.move_to_limit(1, -to_limit_speed)
        
class CustomTool(BaseTool): 
    #right click
    def normal_right_down(self, event):
        '''
        on right click
        '''
        print event            
            
class FieldDataController(HasTraits):
    
    model=Instance(FieldData)
    plot_container=Instance(Component)
    plot_data=Instance(ArrayPlotData)
    _image_value = Instance(ImageData)
    renderer = Any()
    
    update = Event
    
    steps_backwards = Int(100)
    steps_side = Int(20)
    steps_up = Int(60)
    steps_per_move = Int(5)
    step_amplitude_side = Int(16)
    step_amplitude_up=Int(25)
    step_amplitude_backwards=Int(50)

    thread_control = Event
    capture_thread=Instance(CaptureThread) 
    label_button_measurment = Str('Start acquisition')
    
    _save_file = File('default.npy', filter=['Numpy files (*.npy)| *.npy'])
    _load_file = File('.npy',  filter=['Numpy files (*.npy) | *.npy', 'All files (*.*) | *.*'])
    # Define the view associated with this controller:
    view = View(HGroup(VGroup('steps_backwards','steps_side','steps_up','steps_per_move'),
                       VGroup('step_amplitude_backwards','step_amplitude_side','step_amplitude_up'),
                       VGroup(Item('thread_control' , label='', editor = ButtonEditor(label_value = 'label_button_measurment')))),
                Item('plot_container',editor=ComponentEditor(),show_label=False),
                menubar=MenuBar(Menu("_",Action(name="Load data", action="load_file"), # action= ... calls the function, given in the string
                                     Action(name="Save data", action="save_file"), 
                                    '_',
                                    CloseAction,
                                    name="File")),
                resizable=True,
                width=700)
    
    save_file_view = View(Item('_save_file'), 
                          buttons=OKCancelButtons, 
                          kind='livemodal',  # NB must use livemodal, plot objects don't copy well
                          width=400,
                          resizable=True)
    load_file_view = View(Item('_load_file'), 
                          buttons=OKCancelButtons, 
                          kind='livemodal',  # NB must use livemodal, plot objects don't copy well
                          width=400,
                          resizable=True)  
    
    def __init__(self,*args, **kw):
        super(FieldDataController, self).__init__(*args, **kw)
        #self.plotdata = ArrayPlotData(x = self.model.index, y = self.model.data)

        self.model.intens_xy = array([[]])
        self.model.intens_xz = array([[]])
        self.model.intens_yz = array([[]])
        # Create a plot data obect and give it this data
        self.create_plot_component()
        
    def create_plot_component(self):
        self.plot_data = ArrayPlotData()
        self.plot_data.set_data("imagedata", self.model.intens_xy)
        self.plot_data.set_data('vert_image',self.model.intens_yz)
        # Create a contour polygon plot of the data
        plot = Plot(self.plot_data)
        plot.title = 'Horizontal plane'
        plot.padding=5
        plot.padding_top = 22
        plot.padding_left=25
        plot.padding_bottom=20
        my_plot = plot.img_plot("imagedata", name='my_plot', # xbounds=x,#ybounds=y,
                             colormap=jet, hide_grids=True)[0]
        
        colormap = my_plot.color_mapper
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)      
        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom
        colorbar.padding_left = 30
        colorbar.padding_right = 35                                         
                             
                             
        rplot = Plot(self.plot_data)
        rplot.title = 'Vertical plane'
        rplot.padding=plot.padding
        rplot.padding_top = plot.padding_top
        rplot.padding_left = plot.padding_left
        rplot.padding_bottom = plot.padding_bottom   
        my_plot = rplot.img_plot('vert_image',name='vert_plot',colormap=jet)[0]
        colormap = my_plot.color_mapper
        colorbar_rplot = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                        color_mapper=colormap,
                        plot=my_plot,
                        orientation='v',
                        resizable='v',
                        width=25,
                        padding=0)      
        colorbar_rplot.padding_top = plot.padding_top
        colorbar_rplot.padding_bottom = plot.padding_bottom
        colorbar_rplot.padding_right = 20
        colorbar_rplot.padding_left = 30    
          
        container = HPlotContainer(use_backbuffer = True)
        container.add(plot)
        container.add(colorbar)
        container.add(rplot)
        container.add(colorbar_rplot)
        self.plot_container = container
            
    def _thread_control_fired(self):
        # if not self.running:
        if self.capture_thread and self.capture_thread.isAlive():
            self.capture_thread.wants_abort = True
            self.label_button_measurment = 'Start acquisition'
        else:
            self.capture_thread = CaptureThread()
            self.capture_thread.wants_abort = False
            self.capture_thread.fd = self.model
            self.capture_thread.plotdata= self.plot_data
            self.capture_thread.step_amplitude_side = self.step_amplitude_side
            self.capture_thread.step_amplitude_up = self.step_amplitude_up
            self.capture_thread.step_amplitude_backwards = self.step_amplitude_backwards
            self.capture_thread.steps_side = self.steps_side
            self.capture_thread.steps_up = self.steps_up
            self.capture_thread.steps_backwards = self.steps_backwards
            self.capture_thread.steps_per_move = self.steps_per_move
            self.capture_thread.start()
            self.label_button_measurment = 'Stop acquisition'
            
    def _step_amplitude_changed(self):
        if self.capture_thread:
            self.capture_thread.stepamplitude = self.step_amplitude
    
    def _update_fired(self):
        self.create_plot_component()
            
    @on_trait_change('model.intens_xy')        
    def update_plot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            self.create_plot_component()
            
    @on_trait_change('model.intens_xz')        
    def update_rplot(self,name,old,new):
        if self.plot_data and new.ndim > 1:
            self.create_plot_component()

    def save_file(self):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.edit_traits(view='save_file_view')
        if ui.result == True:
            save(self._save_file, self.model.intens_xy)
            save(self._save_file + '_vertical',self.model.intens_xy)
            
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        import easygui
        tmp = easygui.fileopenbox(title = "Choose your file",default="*.npy")
        #ui = self.edit_traits(view='load_file_view')
        if tmp:
            self._load_file=tmp
            try:
                self.model.intens_xy = load(self._load_file)
            except:
                print 'Loading the file failed'
            
        
    
ui = FieldDataController(model=FieldData(intens_xy=array([[0][0]])))
ui.configure_traits(view='view')
