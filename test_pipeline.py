from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import html, vuetify
from paraview.simple import *
from trame.widgets import paraview as pvwidgets

# Base class for visualizations
class BaseVisualization:
    def __init__(self, server, state):
        self.server = server
        self.state = state

    def layout(self, parent):
        raise NotImplementedError("Subclasses must implement layout().")

#  visualization subclass 1
class Visualization1(BaseVisualization):
    def layout(self, parent):
        # Here, create a placeholder visualization.
        #  replace with the ParaView view or custom widget.
        with parent:
            with vuetify.VCard(style="height: 900px; background-color: #EEE;"):
                html.Div("Visualization 1 Display", style="text-align: center; padding-top: 180px;")

#  visualization subclass 2
class Visualization2(BaseVisualization):
    def layout(self, parent):
        with parent:
            with vuetify.VCard(style="height: 400px; background-color: #DDEEFF;"):
                html.Div("Visualization 2 Display", style="text-align: center; padding-top: 180px;")


# Main Application Class
class VisualizationApp:
    def __init__(self, client_type="vue2"):
        # Create the server with the desired Vue client type
        self.server = get_server(client_type=client_type)
        self.state = self.server.state

        # Define the application state properties
        self.state.visualization = "Visualization 1"
        self.state.particle_size = 5
        self.state.options = ["Visualization 1", "Visualization 2"]

        # Instantiate visualization objects keyed by their names
        self.visualizations = {
            "Visualization 1": Visualization1(self.server, self.state),
            "Visualization 2": Visualization2(self.server, self.state)
        }

        # Build the UI layout
        self.build_layout()

        # Register a callback for when the selected visualization changes
        self.server.change("visualization")(self.update_visualization)

    def build_layout(self):
        # Create the main layout using a SinglePageLayout
        with SinglePageLayout(self.server) as layout:
            layout.title.set_text("")
            with layout.toolbar:
                html.H1("Visualization App", style="margin: 0")
            with layout.content:
                with vuetify.VContainer(fluid=True):
                    with vuetify.VRow():
                        # Left side panel with controls
                        with vuetify.VCol(cols=3):
                            with vuetify.VCard():
                                with vuetify.VCardTitle():
                                    html.H3("Controls")
                                with vuetify.VCardText():
                                    # Dropdown for selecting visualization type
                                    vuetify.VSelect(
                                        v_model=("visualization", self.state.visualization),
                                        items=("options", self.state.options),
                                        label="Select Visualization",
                                    )
                                    # Slider widget shown only for Visualization 1
                                    vuetify.VSlider(
                                        v_model=("particle_size", self.state.particle_size),
                                        min=1,
                                        max=20,
                                        label="Particle Size",
                                        v_if=("visualization === 'Visualization 1'", True),
                                    )
                        # Right main visualization area
                        with vuetify.VCol(cols=9):
                            # We'll assign an ID to the container so we can update it when needed.
                            self.visualization_area = vuetify.VContainer(id="visualization-area")
                            # Initially render the default visualization
                            self.render_visualization()

    def update_visualization(self, visualization, **kwargs):
        # Callback triggered when the visualization selection changes.
        print(f"Switching to {visualization}")
        self.render_visualization()

    def render_visualization(self):
        # Clear the current childre
        self.visualization_area.children = []
        current_vis = self.state.visualization
        # Render the selected visualization
        self.visualizations[current_vis].layout(self.visualization_area)

    def start(self):
        self.server.start()

if __name__ == "__main__":
    app = VisualizationApp(client_type="vue2")
    app.start()
