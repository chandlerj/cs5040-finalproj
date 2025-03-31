import os
from paraview import simple
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import paraview, vuetify3

server = get_server()
state, ctrl = server.state, server.controller


paraview.initialize(server)

# CLI args for loading .pvsm file
parser = server.cli
parser.add_argument("--data", help="Path to state file", dest="data")
args = parser.parse_args()

# Load the ParaView state file
full_path = os.path.abspath(args.data)
working_directory = os.path.dirname(full_path)

simple.LoadState(
    full_path,
    data_directory=working_directory,
    restrict_to_data_directory=True,
)
view = simple.GetActiveView()
view.MakeRenderWindowInteractor(True)
view.GetRenderWindow().SetOffScreenRendering(1)


# Find the IsoVolume filter
iso_filter = None
for key, proxy in simple.GetSources().items():
    if proxy.GetXMLName() == "IsoVolume":
        iso_filter = proxy
        break

if iso_filter is None:
    raise RuntimeError("No IsoVolume filter found in state file.")

initial_range = list(iso_filter.ThresholdRange)
state.min_threshold = initial_range[0] if initial_range else 0.0


# === Extract time steps ===
reader = simple.GetAnimationScene()
reader.UpdateAnimationUsingDataTimeSteps()

time_steps = []
# Try getting time steps from any time-aware source
sources = simple.GetSources()
for key in sources:
    try:
        tsteps = sources[key].TimestepValues
        if tsteps:
            time_steps = list(tsteps)
            break
    except AttributeError:
        continue

# Fallback to scene time steps
if not time_steps and hasattr(reader, "TimeKeeper") and hasattr(reader.TimeKeeper, "TimestepValues"):
    time_steps = list(reader.TimeKeeper.TimestepValues)

# Set default slider state
state.time_value = time_steps[0] if time_steps else 0.0

# === Time update callback ===
@state.change("time_value")
def update_time_value(time_value, **kwargs):
    reader.AnimationTime = time_value
    view.StillRender()


@state.change("min_threshold")
def update_iso_range(min_threshold, **kwargs):
    old_range = list(iso_filter.ThresholdRange)
    if old_range[0] != min_threshold:
        iso_filter.ThresholdRange = [min_threshold, old_range[1]]
        view.StillRender()


# Build the UI
with SinglePageLayout(server) as layout:
    layout.title.set_text("ParaView State Viewer")
    layout.icon.click = "$refs.view.resetCamera()"
    

    with layout.toolbar:
        if time_steps:
            vuetify3.VSlider(
                v_model=("time_value", state.time_value),
                min=time_steps[0],
                max=time_steps[-1],
                step=(time_steps[1] - time_steps[0]) if len(time_steps) > 1 else 1,
                label="Timestep",
                hide_details=True,
                class_="ma-4",
            )

        vuetify3.VSlider(
            v_model=("min_threshold", state.min_threshold),
            min=0,                  # Update this to reflect your data range
            max=100,
            step=0.1,
            label="Min Threshold",
            hide_details=True,
            class_="ma-4",
        )
        

    with layout.content:
        with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
            paraview.VtkRemoteView(view, ref="view")

# Start the app
if __name__ == "__main__":
    server.start()

