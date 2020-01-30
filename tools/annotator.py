from pathlib import Path
from os.path import join
from io import BytesIO
from PIL import Image
from base64 import b64encode
import tensorflow as tf
import numpy as np
from IPython.display import display, HTML
from object_detection.utils import dataset_util
try:
    from google.colab import output
except:
    print("Not on google colab")
import uuid


class Annotator:

    _template_uri = join(Path(__file__).parent.absolute(), "_static", "annotator.rs")

    def __init__(self, folder, parser, sample_size, out_file):
        self.folder = folder
        self.parser = parser
        self.writer = tf.io.TFRecordWriter(out_file)
        self.sample_size = sample_size
        self.template = Path(self._template_uri).read_text()
        self.prev = None
        self.im_buffer = None

    def annotate(self, image):
        _next = Annotator.register_button(self._save)
        _previous = Annotator.register_button(self._previous)
        _skip = Annotator.register_button(self._next)
        self.im_buffer = Annotator.parse_image(image)
        im_base64 = b64encode(self.im_buffer).decode('utf-8')
        display(HTML(self.template.format(image=im_base64, next=_next,
                                          previous= _previous, skip=_skip )))

    def _next(self):
        example = iter(self.parser.take(self.sample_size)).__next__()
        rgb = example[0][0].numpy()[:, :, 0:3]
        rgb = np.interp(rgb, (rgb.min(), rgb.max()), (0, 255))
        self.prev = rgb[..., ::-1].astype("uint8")
        self.annotate(self.prev)

    def _previous(self):
        self.annotate(self.prev)

    def _save(self, xmins, xmaxs, ymins, ymaxs):
        TFExample(self.im_buffer, xmins, xmaxs, ymins, ymaxs)
        self.writer.write(TFExample.tf_example)
        self._next()

    @staticmethod
    def register_button(callback):
        callback_id = 'button-' + str(uuid.uuid4())
        output.register_callback(callback_id, callback)
        return callback_id


    @staticmethod
    def parse_image(image):
        img = Image.fromarray(image)
        buffered = BytesIO()
        img.save(buffered, format="png")
        return buffered.getvalue()


# To be refactored later into the tf_io file
class TFExample:

    _height = 512
    _width = 512
    _im_format = b'png'
    _classes_text = ['Solar']
    _classes = [1]

    def __init__(self, im_buffer, xmins, xmaxs, ymins, ymaxs):
        self.tf_example = tf.train.Example(features=tf.train.Features(feature={
            'image/height': dataset_util.int64_feature(self._height),
            'image/width': dataset_util.int64_feature(self._width),
            'image/encoded': dataset_util.bytes_feature(im_buffer),
            'image/format': dataset_util.bytes_feature(self._im_format),
            'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
            'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
            # 'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
            'image/object/class/label': dataset_util.int64_list_feature(self._classes),
            }))


class InvokeButton(object):

    def __init__(self, title, callback):
        self._title = title
        self._callback = callback

    def html(self):
        callback_id = 'button-' + str(uuid.uuid4())
        output.register_callback(callback_id, self._callback)

        template = """<button id="{callback_id}" class="" >{title}</button>
            <script>
            document.querySelector("#{callback_id}").onclick = (e) => {{
               google.colab.kernel.invokeFunction('{callback_id}', [], {{}})
             e.preventDefault();
          }};
        </script>"""
        html = template.format(title=self._title, callback_id=callback_id)
        return html