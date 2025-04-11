import os

class BaseVisualization:
    def __init__(self, statefile, datapath, trame_state):
        
        if type(self) == BaseVisualization:
            raise NotImplementedError("BaseVisualization is an abstract class. Please implement your own concrete visualization using this class")
        self.statepath = os.path.abspath(os.path.join("state_files", statefile))
        self.datapath = os.path.abspath(os.path.join("data", datapath))
        self.view = None
        self.scene = None
        self.sources = {}
        self.filters = {}
        self.time_steps = []
        self.trame_state = trame_state

    def load(self):
        raise NotImplementedError("You must define your own load() function in your subclass")

    def render_widgets(self):
        raise NotImplementedError("You must define your own render_widgets() function in your subclass")

    def register_callbacks(self):
        raise NotImplementedError("You must define your own register_callbacks() function in your subclass")

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

    
