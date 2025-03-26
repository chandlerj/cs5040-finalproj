import os
from paraview import simple
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import paraview, vuetify3

server = get_server()
state = server.state

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

# Build the UI
with SinglePageLayout(server) as layout:
    layout.title.set_text("ParaView State Viewer")
    layout.icon.click = "$refs.view.resetCamera()"

    with layout.content:
        with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
            paraview.VtkRemoteView(view, ref="view")

# Start the app
if __name__ == "__main__":
    server.start()

