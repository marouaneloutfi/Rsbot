from keras.models import Model
from keras.layers import Input, BatchNormalization, Activation, Dropout
from keras.layers import Conv2D, Conv2DTranspose
from keras.layers import MaxPooling2D
from keras.layers import concatenate


class Unet:
    """
        A Unet inspired architecture based on the referenced paper
        - https://arxiv.org/abs/1505.04597 - U-Net: Convolutional Networks for Biomedical Image Segmentation

    """
    def __init__(self, input_shape, n_base_filters, num_classes=1, dropout=0.25, depth=3, pool_shape=(2, 2),
                 batchnorm=True):
        self.input_shape = input_shape
        self.n_base_filters = n_base_filters
        self.dropout = dropout
        self.depth = depth
        self.pool_shape = pool_shape
        self.batchnorm = batchnorm
        self.num_classes = num_classes

    def get_model(self):
        inputs = Input(self.input_shape)
        current_layer = inputs
        conv_blocks = []

        # Encoder block
        for i in range(self.depth - 1):
            n_filters = self.n_base_filters*(2**(i+1))
            conv_block = self.create_conv2d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3))
            pool_layer = MaxPooling2D(self.pool_shape, name="max_pool_"+str(i))(conv_block)
            current_layer = Dropout(self.dropout*0.5)(pool_layer)
            conv_blocks.append(conv_block)

        n_filters = self.n_base_filters(2**(self.depth+1))
        current_layer = self.create_conv2d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3))

        # Decoder block
        for i, conv_block in reversed(list(enumerate(conv_blocks))):
            n_filters = self.n_base_filters*(2**(i+1))
            deconv_block = self.create_deconv2d_block(current_layer, conv_block, n_filters, (3, 3))
            deconv_block = Dropout(self.dropout)(deconv_block)
            current_layer = self.create_conv2d_block(deconv_block, n_filters=n_filters, kernel_shape=(3, 3))

        outputs = Conv2D(self.num_classes, (1, 1), activation='sigmoid', name="output")(current_layer)

        return Model(inputs, outputs)

    def create_conv2d_block(self, input_tensor, n_filters, kernel_shape, activation='relu',
                            name="default"):
        layer = Conv2D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name)(input_tensor)
        if self.batchnorm:
            layer = BatchNormalization(layer)
        layer = Activation(activation)(layer)

        # second layer of the convolutional block
        layer = Conv2D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name)(layer)
        if self.batchnorm:
            layer = BatchNormalization(layer)
        return Activation(activation)(layer)

    @staticmethod
    def create_deconv2d_block(input_tensor, conv_block, n_filters, kernel_shape, strides=(2, 2)):
        up_layer = Conv2DTranspose(n_filters, kernel_size=kernel_shape, strides=strides, padding='same')(input_tensor)
        return concatenate(up_layer, conv_block)
