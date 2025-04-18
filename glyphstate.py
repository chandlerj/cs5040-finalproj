# from vizstate import VizState
from trame.widgets import vuetify3
from paraview import simple
from trame.app import get_server
import os

from base_visualization import BaseVisualization

# ---------------------
# Modular VizState class
# ---------------------
class GlyphState(BaseVisualization):

    def __init__(self, statefile, datapath, trame_state):
        super().__init__(statefile, datapath, trame_state)

    def load(self):
        # Load state (this will still create a new view)
        simple.LoadState(
            self.statepath,
            data_directory=self.datapath,
            restrict_to_data_directory=True,
        )
    
 
        self.view = simple.GetActiveView()
        self.view.MakeRenderWindowInteractor(True)
        self.view.GetRenderWindow().SetOffScreenRendering(1)

  
        self.scene = simple.GetAnimationScene()
        self.scene.UpdateAnimationUsingDataTimeSteps()
    
        self.sources = simple.GetSources()
   
        self.view.ResetCamera()
        self.view.StillRender()
    
        self.time_steps = self.extract_time_steps()
        self.trame_state.time_value = self.time_steps[0] if self.time_steps else 0.0

    def render_widgets(self):
        widgets = []

        if self.time_steps:
            widgets.append(
                vuetify3.VSlider(
                    v_model=("time_value", self.trame_state.time_value),
                    min=self.time_steps[0],
                    max=self.time_steps[-1],
                    step=(self.time_steps[1] - self.time_steps[0]) if len(self.time_steps) > 1 else 1,
                    label="Timestep",
                    ticks=True,
                    thumb_label=True,
                    hide_details=False,
                    class_="ma-4",
                )
            )

        return widgets

    def register_callbacks(self):
        server = get_server()
        ctrl = server.controller
        @self.trame_state.change("time_value")
        def update_time(time_value, **kwargs):
            self.scene.AnimationTime = time_value
            self.view.StillRender()
            ctrl.view_update()


