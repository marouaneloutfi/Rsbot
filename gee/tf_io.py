import tensorflow as tf
from .utils import get_selectors


def get_columns(features, kernel_shape):
    return [tf.io.FixedLenFeature(shape=kernel_shape, dtype=tf.float32) for k in features]


class TfDatasetParser:
    _bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']

    def __init__(self, kernel_size, response):
        self.features = get_selectors(self._bands) + response
        columns = get_columns(self.features, [kernel_size, kernel_size])
        self.feature_dic = dict(zip(self.features, columns))

    def get_dataset(self, tf_dir,kernel_size, shuffle=True):
        """Get the preprocessed training dataset
      Returns:
        A tf.data.Dataset of training data.
      """
        dataset = self.parse_dataset(tf_dir)
        if shuffle:
            dataset = dataset.shuffle(kernel_size).batch(kernel_size).repeat()
        else:
            dataset = dataset.batch(1).repeat()
        return dataset

    def parse_dataset(self, pattern):
        glob = tf.gfile.Glob(pattern)
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
            return [tempo_slices[:, :, i:i + 8] for i in range(0, len(get_selectors(self.bands)), 8)]






