from trame.widgets import vuetify3
from paraview import simple
import os
from trame.app import get_server
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

        # Extract clip y origin
        self.filters["clip"] = self.find_filter("Clip")
        if not self.filters["clip"]:
            raise RuntimeError("No Clip filter found in state file.")
        clip_origin = list(self.filters["clip"].ClipType.Origin)
        self.trame_state.clip_y_origin = clip_origin[1] if clip_origin else 0.0

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
                    ticks=True,
                    thumb_label=True,
                    hide_details=False,
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
                ticks=True,
                thumb_label=True,
                hide_details=False,
                class_="ma-4",
            )
        )

        widgets.append(
            vuetify3.VSlider(
                v_model=("clip_y_origin", self.trame_state.clip_y_origin),
                min=-5,
                max=5,
                step=0.01,
                label="Clip Y Origin",
                ticks=True,
                thumb_label=True,
                hide_details=True,
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

        @self.trame_state.change("min_threshold")
        def update_threshold(min_threshold, **kwargs):
            # Instead of using ThresholdRange, update LowerThreshold directly.
            current_lower = self.filters["threshold"].LowerThreshold
            if current_lower != min_threshold:
                self.filters["threshold"].LowerThreshold = min_threshold
                # For a threshold between lower and upper values, set the method to "Between"
                self.filters["threshold"].ThresholdMethod = "Between"
                self.view.StillRender()
                ctrl.view_update()

        @self.trame_state.change("clip_y_origin")
        def update_clip_y_origin(clip_y_origin, **kwargs):
            clip = self.filters["clip"]
            origin = list(clip.ClipType.Origin)
            origin[1] = clip_y_origin
            clip.ClipType.Origin = origin
            self.view.StillRender()
            ctrl.view_update()



