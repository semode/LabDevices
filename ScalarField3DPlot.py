# Authors: Prabhu Ramachandran <prabhu [at] aero.iitb.ac.in>
# Copyright (c) 2007, Enthought, Inc.
# License: BSD Style.

# Standard imports.
from numpy import sqrt, sin, mgrid, ogrid, random, mgrid, asarray, load

# Enthought imports.
from traits.api import HasTraits, Instance, Property, Enum, Str
from traits.api import HasTraits, Instance, Property, Enum, Int
from traitsui.api import View, Item, HSplit, VSplit, InstanceEditor
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.engine_view import EngineView
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi import mlab
from enthought.mayavi.sources.api import ArraySource 

from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator
from mayavi.modules.api import Outline, Surface, Volume, ScalarCutPlane, ImagePlaneWidget

class ScalarField3DPlot_GUI(HasTraits):

    # The scene model.
    scene = Instance(MlabSceneModel, ())
    # The mayavi engine view.
    engine_view = Instance(EngineView)

    src = Instance(ArraySource)

    file_name = Str('default.npy')


    view = View(HSplit(Item(name='engine_view',
                                   style='custom',
                                   resizable=True,
                                   show_label=False
                                   ),
                               Item(name='scene',
                                    editor=SceneEditor(),
                                    show_label=False,
                                    resizable=True,
                                    width=400,
                                    height=400
                                    )
                        ),
                        menubar=MenuBar(Menu(Separator(),
                                             Action(name="Load Numpy-data", action="load_file"), # action= ... calls the function, given in the string
                                             Separator(),
                                             CloseAction,
                                             name="File")),
                resizable=True,
                scrollable=True
                )
    
    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.engine_view = EngineView(engine=self.scene.engine)

        # Hook up the current_selection to change when the one in the engine
        # changes.  This is probably unnecessary in Traits3 since you can show
        # the UI of a sub-object in T3.
        #self.scene.engine.on_trait_change(self._selection_change,
        #                                  'current_selection')

        self.generate_data_mayavi()

        
    def load_file(self):
        """
        Callback for the 'Load Image' menu option.
        """
        import easygui
        tmp = easygui.fileopenbox(title = "Choose your file",default="*.npy")
        if tmp:
            try:
                self.file_name = tmp
                self.set_data(load(self.file_name))
            except:
                print 'Loading file failed'
    
    def generate_data_mayavi(self):
        """Shows how you can generate data using mayavi instead of mlab."""
        #from mayavi.sources.api import ParametricSurface
        x, y, z = ogrid[-10:10:20j, -10:10:20j, -10:10:20j]
        s = sin(x*y*z)/(x*y*z)
        e = self.scene.engine                     
        self.src = ArraySource()
        self.src.scalar_data = s
        e.add_source(self.src)
        self.v = Volume()
        #change opacity values
        from tvtk.util.ctf import PiecewiseFunction
        otf = PiecewiseFunction()
        otf.add_point(0, 0)
        otf.add_point(0.6*255, 0)
        otf.add_point(0.8*255,1)
        self.v._otf = otf
        self.v.volume_property.set_scalar_opacity(otf)
        e.add_module(self.v)
        cp = ScalarCutPlane()
        e.add_module(cp)

        #cp.implicit_plane.normal = 0,0,1
        #self.src.scalar_data  = random.random((20,20,20))
    
    def set_data(self, data):
        self.src.scalar_data = data
        
    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def _get_current_selection(self):
        return self.scene.engine.current_selection
    
if __name__ == '__main__':
    m = ScalarField3DPlot_GUI()
    m.configure_traits()