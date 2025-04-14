from trame.widgets import vuetify3
from paraview import simple
import os

from base_visualization import BaseVisualization

class ClusteredState(BaseVisualization):

    def __init__(self, statefile, datapath, trame_state):
        super().__init__(statefile, datapath, trame_state)

    def load(self):
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
        # Look for the new "Threshold" filter
        self.filters["threshold"] = self.find_filter("Threshold")

        if not self.filters["threshold"]:
            raise RuntimeError("No Threshold filter found in state file.")

        # fetch LowerThreshold and UpperThreshold:
        lower = self.filters["threshold"].LowerThreshold
        upper = self.filters["threshold"].UpperThreshold

        # Set the initial state value to the lower threshold.
        self.trame_state.min_threshold = lower if lower is not None else 0.0

        self.time_steps = self.extract_time_steps()
        self.trame_state.time_value = self.time_steps[0] if self.time_steps else 0.0

    def render_widgets(self):
        widgets = []
        # Time slider remains unchanged.
        if self.time_steps:
            widgets.append(
                vuetify3.VSlider(
                    v_model=("time_value", self.trame_state.time_value),
                    min=self.time_steps[0],
                    max=self.time_steps[-1],
                    step=(self.time_steps[1] - self.time_steps[0]) if len(self.time_steps) > 1 else 1,
                    label="Timestep",
                    hide_details=True,
                    class_="ma-4",
                )
            )

        upper = self.filters["threshold"].UpperThreshold
        max_val = upper if upper is not None else 100

        widgets.append(
            vuetify3.VSlider(
                v_model=("min_threshold", self.trame_state.min_threshold),
                min=0,
                max=max_val,
                step=0.1,
                label="Min Threshold",
                hide_details=True,
                class_="ma-4",
            )
        )

        return widgets

    def register_callbacks(self):
        @self.trame_state.change("time_value")
        def update_time(time_value, **kwargs):
            self.scene.AnimationTime = time_value
            self.view.StillRender()

        @self.trame_state.change("min_threshold")
        def update_threshold(min_threshold, **kwargs):
            # Instead of using ThresholdRange, update LowerThreshold directly.
            current_lower = self.filters["threshold"].LowerThreshold
            if current_lower != min_threshold:
                self.filters["threshold"].LowerThreshold = min_threshold
                # For a threshold between lower and upper values, set the method to "Between"
                self.filters["threshold"].ThresholdMethod = "Between"
                self.view.StillRender()
