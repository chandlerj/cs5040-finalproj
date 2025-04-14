import os, sys, json
from paraview import simple
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import paraview, vuetify3, html
from isovolumestate import IsoVolumeState
from cluster_iso_state import ClusteredState
from glyphstate import GlyphState

# select visualization
default_viz = "Point Cloud"
try:
    with open("viz_config.json") as f:
        default_viz = json.load(f).get("selected", default_viz)
except FileNotFoundError:
    print(f"Configuration file viz_config.json not found, continuing with default: {default_viz}")
    # Continue with the default visualization
    pass


# trame setup
server = get_server()
state, ctrl = server.state, server.controller
paraview.initialize(server)


visualizations = {
        "Point Cloud": IsoVolumeState("isostate.pvsm", "run01", state),
        "Glyphs": GlyphState("glyphstate.pvsm", "run01", state),
        "Clustered": ClusteredState("clustering_DBSCAN.pvsm", "run01_DBSCAN", state),
}
curr_viz = visualizations[default_viz]

state.viz_labels = ["Point Cloud", "Glyphs", "Clustered"]
state.curr_viz_label = default_viz

# Instantiate and load the state
curr_viz.load()
curr_viz.register_callbacks()


ctrl.filter_controls = lambda: curr_viz.render_widgets()


def update_viz_render(**kwargs):
    """
    Dump the selected state to a json file and reload
    the server with the new state selected
    """
    try:
        with open("viz_config.json") as f:
            selected = json.load(f).get("selected")
    except FileNotFoundError:
        selected = None

    if selected == state.curr_viz_label:
        print("Selected visualization already loaded. Aborting reboot...")
        return  # no change, skip restart

    with open("viz_config.json", "w") as f:
        json.dump({"selected": state.curr_viz_label}, f)

    print(f"[Trame] Restarting with new selection: {state.curr_viz_label}")
    sys.stdout.flush()

    os.execv(sys.executable, [sys.executable] + sys.argv)

server.change("curr_viz_label")(update_viz_render)

# Build UI
with SinglePageLayout(server) as layout:
    layout.title.set_text("Modular ParaView State Viewer")

    with layout.content:
        with vuetify3.VContainer(fluid=True, classes="fill-height"):
            with vuetify3.VRow(classes="fill-height", no_gutters=True):
                with vuetify3.VCol(cols=3, classes=""):
                    with vuetify3.VCardText():
                        vuetify3.VSelect(
                                v_model=("curr_viz_label", state.curr_viz_label),
                                items=("viz_labels", state.viz_labels),
                                label="Select Visualization"
                                )
                    with vuetify3.VCardTitle():
                        html.H3("Controls")
                    ctrl.filter_controls()
                with vuetify3.VCol(cols=9, classes=""):
                    with vuetify3.VContainer(fluid=True, classes="fill-height"):
                        paraview.VtkRemoteView(curr_viz.view, ref="view", classes="")

# Start server
if __name__ == "__main__":
    server.start()
