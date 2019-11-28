from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, BatchNormalization, Activation, Dropout
from tensorflow.keras.layers import Conv3D, Conv3DTranspose, Conv2D, Reshape
from tensorflow.keras.layers import MaxPooling3D
from tensorflow.keras.layers import concatenate


class Unet3D:
    """
        A Unet inspired architecture based on the reference
        d paper
        - https://arxiv.org/abs/1505.04597 - U-Net: Convolutional Networks for Biomedical Image Segmentation

    """
    def __init__(self, input_shape, n_base_filters, num_classes=1, dropout=0.25, depth=3, pool_shape=(2, 2, 2),
                 batchnorm=True):
        self.input_shape = input_shape
        self.n_base_filters = n_base_filters
        self.dropout = dropout
        self.depth = depth
        self.pool_shape = pool_shape
        self.batchnorm = batchnorm
        self.num_classes = num_classes

    def get_model(self, final_activation='softmax'):
        inputs = Input(self.input_shape)
        current_layer = inputs
        conv_blocks = []

        # Encoder block
        for i in range(self.depth):
            n_filters = self.n_base_filters*(2**i)
            conv_block = self.create_conv3d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3, 3), name="convBlock0"+str(i))
            pool_layer = MaxPooling3D(self.pool_shape, name="max_pool_"+str(i))(conv_block)
            current_layer = Dropout(self.dropout*0.5)(pool_layer)
            conv_blocks.append(conv_block)

        n_filters = self.n_base_filters*(2**self.depth)
        current_layer = self.create_conv3d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3, 3))

        # Decoder block
        for i, conv_block in reversed(list(enumerate(conv_blocks))):
            n_filters = self.n_base_filters*(2**(i+1))
            deconv_block = self.create_deconv3d_block(current_layer, conv_block, n_filters, (3, 3, 3), name="deconvBlock"+str(i))
            deconv_block = Dropout(self.dropout)(deconv_block)
            current_layer = self.create_conv3d_block(deconv_block, n_filters=n_filters, kernel_shape=(3, 3, 3), name="convBlock1"+str(i))
        p = MaxPooling3D((1, 1, 3), name='max_block_8')(current_layer)
        r = Reshape((self.input_shape[0], self.input_shape[1], self.n_base_filters*2))(p)
        outputs = Conv2D(self.num_classes, (1, 1), activation=final_activation, name="output")(r)

        return Model(inputs, outputs)

    def create_conv3d_block(self, input_tensor, n_filters, kernel_shape, activation='relu',
                            name="default"):
        layer = Conv3D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name+'0')(input_tensor)
        if self.batchnorm:
            layer = BatchNormalization()(layer)
        layer = Activation(activation)(layer)

        # second layer of the convolutional block
        layer = Conv3D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name+'1')(layer)
        if self.batchnorm:
            layer = BatchNormalization()(layer)
        return Activation(activation)(layer)

    @staticmethod
    def create_deconv3d_block(input_tensor, conv_block, n_filters, kernel_shape, strides=(2, 2, 2), name="default"):
        up_layer = Conv3DTranspose(n_filters, kernel_size=kernel_shape, strides=strides, padding='same', name=name)(input_tensor)
        return concatenate([up_layer, conv_block])
