from paraview.web import venv  # Available in PV 5.10-RC2+
from paraview import simple

from pathlib import Path
from trame.app import get_server
from trame.widgets import vuetify, paraview, client
from trame.ui.vuetify import SinglePageLayout

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Preload paraview modules onto server
paraview.initialize(server)


# -----------------------------------------------------------------------------
# ParaView code
# -----------------------------------------------------------------------------


def load_data(**kwargs):
    # CLI
    args, _ = server.cli.parse_known_args()

    full_path = str(Path(args.data).resolve().absolute())
    working_directory = str(Path(args.data).parent.resolve().absolute())

    # ParaView
    simple.LoadState(
        full_path,
        data_directory=working_directory,
        restrict_to_data_directory=True,
    )
    view = simple.GetActiveView()
    view.MakeRenderWindowInteractor(True)
    simple.Render(view)

    # Get Contour1 filter
    contour = simple.FindSource("Contour1")
    if not contour:
        raise ValueError("Contour1 filter not found in the state file")

    # Determine array and data range
    input_data = contour.Input
    array = None
    if contour.ContourBy == 'POINTS':
        array_name = contour.SelectInputScalars
        array = input_data.PointData.GetArray(array_name)
    elif contour.ContourBy == 'CELLS':
        array_name = contour.SelectInputScalars
        array = input_data.CellData.GetArray(array_name)

    if not array:
        # Fallback to first point data array
        array = input_data.PointData.GetArray(0)

    data_range = array.GetRange() if array else [0.0, 1.0]

    # Initialize state variables
    state.contour_value = contour.Isosurfaces[0]
    state.contour_min = data_range[0]
    state.contour_max = data_range[1]

    # Define contour update function
    def update_contour():
        contour = simple.FindSource("Contour1")
        if contour:
            contour.Isosurfaces = [state.contour_value]
            ctrl.view_update()

    ctrl.update_contour = update_contour

    # HTML
    with SinglePageLayout(server) as layout:
        layout.icon.click = ctrl.view_reset_camera
        layout.title.set_text("ParaView State Viewer")

        with layout.content:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                html_view = paraview.VtkRemoteView(view)
                ctrl.view_reset_camera = html_view.reset_camera
                ctrl.view_update = html_view.update

                # Contour slider
                with vuetify.VRow(classes="ma-2"):
                    with vuetify.VCol(cols="12"):
                        vuetify.VSlider(
                            v_model=("contour_value",),
                            min=("contour_min",),
                            max=("contour_max",),
                            step=0.1,
                            label="Contour Value",
                            hide_details=True,
                            dense=True,
                            change=ctrl.update_contour,
                        )


ctrl.on_server_ready.add(load_data)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.cli.add_argument("--data", help="Path to state file", dest="data")
    server.start()