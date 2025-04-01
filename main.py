import os
from paraview import simple
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import paraview, vuetify3

# ---------------------
# Modular VizState class
# ---------------------
class IsoVolumeState:
    def __init__(self, statepath):
        self.statepath = os.path.abspath(statepath)
        self.view = None
        self.scene = None
        self.sources = {}
        self.filters = {}
        self.time_steps = []

    def load(self, trame_state):
        working_dir = os.path.dirname(self.statepath)

        simple.LoadState(
            self.statepath,
            data_directory=working_dir,
            restrict_to_data_directory=True,
        )

        self.view = simple.GetActiveView()
        self.view.MakeRenderWindowInteractor(True)
        self.view.GetRenderWindow().SetOffScreenRendering(1)

        self.scene = simple.GetAnimationScene()
        self.scene.UpdateAnimationUsingDataTimeSteps()

        self.sources = simple.GetSources()
        self.filters["iso"] = self.find_filter("IsoVolume")

        if not self.filters["iso"]:
            raise RuntimeError("No IsoVolume filter found in state file.")

        # Extract threshold range
        threshold_range = list(self.filters["iso"].ThresholdRange)
        trame_state.min_threshold = threshold_range[0] if threshold_range else 0.0

        # Extract time steps
        self.time_steps = self.extract_time_steps()
        trame_state.time_value = self.time_steps[0] if self.time_steps else 0.0

    def find_filter(self, type_name):
        for proxy in self.sources.values():
            if proxy.GetXMLName() == type_name:
                return proxy
        return None

    def extract_time_steps(self):
        for proxy in self.sources.values():
            try:
                t = list(proxy.TimestepValues)
                if t:
                    return t
            except AttributeError:
                continue

        if hasattr(self.scene.TimeKeeper, "TimestepValues"):
            return list(self.scene.TimeKeeper.TimestepValues)

        return []

    def render_widgets(self, trame_state):
        widgets = []

        if self.time_steps:
            widgets.append(
                vuetify3.VSlider(
                    v_model=("time_value", trame_state.time_value),
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
                v_model=("min_threshold", trame_state.min_threshold),
                min=0,
                max=100,
                step=0.1,
                label="Min Threshold",
                hide_details=True,
                class_="ma-4",
            )
        )

        return widgets

    def register_callbacks(self, trame_state):
        @trame_state.change("time_value")
        def update_time(time_value, **kwargs):
            self.scene.AnimationTime = time_value
            self.view.StillRender()

        @trame_state.change("min_threshold")
        def update_threshold(min_threshold, **kwargs):
            old_range = list(self.filters["iso"].ThresholdRange)
            if old_range[0] != min_threshold:
                self.filters["iso"].ThresholdRange = [min_threshold, old_range[1]]
                self.view.StillRender()


# ---------------------
# Trame App Setup
# ---------------------
server = get_server()
state, ctrl = server.state, server.controller
paraview.initialize(server)

# Instantiate and load the state
viz = IsoVolumeState("isostate.pvsm")
viz.load(state)
viz.register_callbacks(state)


ctrl.filter_controls = lambda: viz.render_widgets(state)

# Build UI
with SinglePageLayout(server) as layout:
    layout.title.set_text("Modular ParaView State Viewer")
    layout.icon.click = "$refs.view.resetCamera()"

    with layout.toolbar:
        ctrl.filter_controls()

    with layout.content:
        with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
            paraview.VtkRemoteView(viz.view, ref="view")

# Start server
if __name__ == "__main__":
    server.start()
