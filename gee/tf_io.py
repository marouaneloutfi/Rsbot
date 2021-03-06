import tensorflow as tf
from .utils import get_selectors


def get_columns(features, kernel_shape):
    return [tf.io.FixedLenFeature(shape=kernel_shape, dtype=tf.float32) for _ in features]


class TfDatasetParser:

    def __init__(self, kernel_size, bands, response, n_bands, n_months):
        self.features = get_selectors(bands) + response
        columns = get_columns(self.features, [kernel_size, kernel_size])
        self.feature_dic = dict(zip(self.features, columns))
        self.n_months = n_months
        self.n_bands = n_bands

    def get_dataset(self, tf_dir, n_samples, batch_size, shuffle=True):
        """Get the preprocessed dataset
      Returns:
        A tf.data.Dataset of the shards in the folder specified
      """
        dataset = self.parse_dataset(tf_dir)
        if shuffle:
            dataset = dataset.shuffle(n_samples).batch(batch_size).repeat()
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
        outputs = stacked[self.n_bands*self.n_months:]
        inputs = tf.stack([stacked[i:i + self.n_bands] for i in range(0, self.n_months*self.n_bands, self.n_bands)], axis=0)

        return tf.transpose(inputs, [2, 3, 1, 0]), tf.transpose(outputs, [1, 2, 0])

    def head_dataset(self, dataset, tempo=False):
        if tempo:
            example = iter(dataset.take(1)).next()
            tempo_slices = example[0][0].numpy()[:, :, :len(get_selectors(self._bands))]
            return [tempo_slices[:, :, i:i + 8] for i in range(0, len(get_selectors(self._bands)), 8)]
