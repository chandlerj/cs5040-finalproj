import os
from paraview import simple
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import paraview, vuetify3, html
from isovolumestate import IsoVolumeState

# ---------------------
# Trame App Setup
# ---------------------
server = get_server()
state, ctrl = server.state, server.controller
paraview.initialize(server)


visualizations = {
        "Point Cloud": IsoVolumeState("isostate.pvsm", state)
}
curr_viz = visualizations['Point Cloud']

state.viz_labels = ["Point Cloud"]
state.curr_viz_label = "Point Cloud"

# Instantiate and load the state
curr_viz.load()
curr_viz.register_callbacks()


ctrl.filter_controls = lambda: curr_viz.render_widgets()


def update_viz_render(**kwargs):
    curr_viz = visualizations[state.curr_viz_label]
    ctrl.filter_controls = lambda: curr_viz.render_widgets()


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
