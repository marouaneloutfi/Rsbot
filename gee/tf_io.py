import tensorflow as tf
import numpy as np
from .utils import get_selectors

tf.enable_eager_execution()


def get_columns(features, kernel_shape):
    return [tf.io.FixedLenFeature(shape=kernel_shape, dtype=tf.float32) for k in features]


class TfDatasetParser:
    _bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']

    def __init__(self, kernel_size, response):
        self.features = get_selectors(self._bands) + response
        columns = get_columns(self.features, [kernel_size, kernel_size])
        self.feature_dic = dict(zip(self.features, columns))

    def get_dataset(self, tf_dir, kernel_size, shuffle=True):
        """Get the preprocessed dataset
      Returns:
        A tf.data.Dataset of the shards in the folder specified
      """
        dataset = self.parse_dataset(tf_dir)
        if shuffle:
            dataset = dataset.shuffle(kernel_size).batch(kernel_size).repeat()
        else:
            dataset = dataset.batch(1).repeat()
        return dataset

    def parse_dataset(self, pattern):
        glob = tf.io.gfile.glob(pattern)
        dataset = tf.data.TFRecordDataset(glob, compression_type='GZIP')
        dataset = dataset.map(self.parse_tfrecord, num_parallel_calls=5)
        dataset = dataset.map(self.to_tuple, num_parallel_calls=5)
        return dataset

    def parse_tfrecord(self, example_proto):
        return tf.io.parse_single_example(example_proto, self.feature_dic)

    def to_tuple(self, inputs):
        """Function to convert a dictionary of tensors to a tuple of (inputs, outputs).
        Turn the tensors returned by parse_tfrecord into a stack in HWC shape.
        Args:
            inputs: A dictionary of tensors, keyed by feature name.
        Returns:
          A dtuple of (inputs, outputs).
        """
        inputsList = [inputs.get(key) for key in self.features]
        stacked = tf.stack(inputsList, axis=0)
        outputs = stacked[64:]
        inputs = tf.stack([stacked[i:i + 8] for i in range(0, 64, 8)], axis=0)

        return tf.transpose(inputs, [2, 3, 1, 0]), tf.transpose(outputs, [1, 2, 0])

    def head_dataset(self, dataset, tempo=False):
        if tempo:
            example = iter(dataset.take(1)).next()
            tempo_slices = example[0][0].numpy()[:, :, :len(get_selectors(self._bands))]
            return [tempo_slices[:, :, i:i + 8] for i in range(0, len(get_selectors(self._bands)), 8)]



#####  functions to be refactored
def hex_to_rgb(hex_str):
    hex_str = hex_str.strip()

    if hex_str[0] == '#':
        hex_str = hex_str[1:]

    if len(hex_str) != 6:
        raise ValueError('Input #{} is not in #RRGGBB format.'.format(hex_str))

    r, g, b = hex_str[:2], hex_str[2:4], hex_str[4:]
    rgb = [int(n, base=16) for n in [r, g, b]]
    return np.array(rgb)


palette = ['ffd300', '267000', 'ffa5e2', 'a57000', '93cc93', '000000']


def binary_mask(crop_mask):
    bin_mask = []
    for x in crop_mask:
        temp = []
        for y in x:
            crop = 0
            for i, ch in enumerate(y):
                if ch >= y[crop]:
                    crop = i
            if y[crop] < 0.65:
                crop = 5
            temp.append(hex_to_rgb(palette[crop]))
        bin_mask.append(temp)
    return np.array(bin_mask, dtype=np.uint8)


def binary_mask_original(crop_mask):
    bin_mask = []
    for x in crop_mask:
        temp = []
        for y in x:
            crop = 0
            for i, ch in enumerate(y):
                if i in [0, 1]:
                    ch *= 0.7
                if ch >= y[crop]:
                    crop = i
            if y[crop] < 0.65 and crop in [0, 1]:
                crop = 5
            temp.append(hex_to_rgb(palette[crop]))
        bin_mask.append(temp)
    return np.array(bin_mask, dtype=np.uint8)





