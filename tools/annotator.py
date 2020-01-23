from IPython.display import display, HTML
from pathlib import Path
from os.path import join

def read_file(template_uri):
    t = open(template_uri, 'r')
    return t.read()


class Annotator:

    _template_uri = join(Path(__file__).parent.absolute(), "_static", "annotator.rs")

    def __init__(self, folder, parser):
        self.folder = folder
        self.parser = folder
        self.template = read_file(self._template_uri)

    def annotate(self, image):
        display(HTML(self.template % image))

