# from vizstate import VizState
from trame.widgets import vuetify3
from paraview import simple
import os
from base_visualization import BaseVisualization
from trame.app import get_server

# ---------------------
# Modular VizState class
# ---------------------
class IsoVolumeState(BaseVisualization):

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

        # Extract threshold range
        self.filters["iso"] = self.find_filter("IsoVolume")

        if not self.filters["iso"]:
            raise RuntimeError("No IsoVolume filter found in state file.")

        threshold_range = list(self.filters["iso"].ThresholdRange)
        self.original_threshold_range = threshold_range
        self.trame_state.min_threshold = threshold_range[0] if threshold_range else 0.0
        self.trame_state.max_threshold = threshold_range[1] if threshold_range else 0.0

        # Extract clip x origin
        self.filters["clip"] = self.find_filter("Clip")
        if not self.filters["clip"]:
            raise RuntimeError("No Clip filter found in state file.")
        clip_origin = list(self.filters["clip"].ClipType.Origin)
        self.trame_state.clip_x_origin = clip_origin[0] if clip_origin else 0.0

        # Change color maps
        self.trame_state.color_presets = [
            "Rainbow Uniform",
            "Cool to Warm",
            "Viridis (matplotlib)",
            "Plasma (matplotlib)",
            "Rainbow Desaturated",
            "X Ray",
            "Black-Body Radiation",
        ]
        self.trame_state.color_map = self.trame_state.color_presets[0]

        # Extract time steps
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
                    hide_details=True,
                    class_="ma-4",
                )
            )
        widgets.append(
            vuetify3.VSlider(
                v_model=("clip_x_origin", self.trame_state.clip_x_origin),
                min=-5,
                max=5,
                step=0.01,
                label="Clip X Origin",
                hide_details=True,
                class_="ma-4",
            )
        )

        widgets.append(
            vuetify3.VSlider(
                v_model=("min_threshold", self.trame_state.min_threshold),
                min=self.original_threshold_range[0],
                max=self.original_threshold_range[1],
                step=0.1,
                label="Min Threshold",
                hide_details=True,
                class_="ma-4",
            )
        )


        widgets.append(
            vuetify3.VSlider(
                v_model=("max_threshold", self.trame_state.max_threshold),
                min=self.original_threshold_range[0],
                max=self.original_threshold_range[1],
                step=0.1,
                label="Max Threshold",
                hide_details=True,
                class_="ma-4",
            )
        )

        widgets.append(
            vuetify3.VSelect(
                v_model=("color_map", self.trame_state.color_map),
                items=("color_presets", self.trame_state.color_presets),
                label="Color Map",
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
        def update_min_threshold(min_threshold, **kwargs):
            old_range = list(self.filters["iso"].ThresholdRange)
            if old_range[0] != min_threshold:
                self.filters["iso"].ThresholdRange = [min_threshold, old_range[1]]
                self.view.StillRender()
                ctrl.view_update()

        @self.trame_state.change("max_threshold")
        def update_max_threshold(max_threshold, **kwargs):
            old_range = list(self.filters["iso"].ThresholdRange)
            if old_range[1] != max_threshold:
                self.filters["iso"].ThresholdRange = [old_range[0], max_threshold]
                self.view.StillRender()
                ctrl.view_update()

        @self.trame_state.change("clip_x_origin")
        def update_clip_x_origin(clip_x_origin, **kwargs):
            clip = self.filters["clip"]
            origin = list(clip.ClipType.Origin)
            origin[0] = clip_x_origin
            clip.ClipType.Origin = origin
            self.view.StillRender()
            ctrl.view_update()

        @self.trame_state.change("color_map")
        def update_colormap(color_map, **kwargs):
            concentrationLUT = simple.GetColorTransferFunction('concentration')
            concentrationLUT.ApplyPreset(color_map, True)
            self.view.StillRender()
            ctrl.view_update()


