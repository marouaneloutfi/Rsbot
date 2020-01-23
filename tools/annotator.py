from IPython.display import display, HTML
from pathlib import Path
from os.path import join





class Annotator:

    _template_uri = join(Path(__file__).parent.absolute(), "_static", "annotator.rs")

    def __init__(self, folder, parser):
        self.folder = folder
        self.parser = folder
        self.template = Path(self._template_uri).read_text()

    def annotate(self, image):
        display(HTML(self.template % image))

