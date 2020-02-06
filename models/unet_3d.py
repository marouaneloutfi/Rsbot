from tensorflow.keras.layers import Input, BatchNormalization, Activation, Dropout
from tensorflow.keras.layers import Conv3D, Conv3DTranspose, Conv2D, Reshape
from tensorflow.keras.layers import MaxPooling3D
from tensorflow.keras.layers import concatenate
from .experiment import RsModel


class Unet3D:
    """
        A Unet inspired architecture based on the reference
        d paper
        - https://arxiv.org/abs/1505.04597 - U-Net: Convolutional Networks for Biomedical Image Segmentation

    """
    def __init__(self, model_info, save_db=True):
        self.save_db = save_db
        self.model_info = model_info

    def get_model(self, db_file):

        model = RsModel(db_file)

        inputs = Input(self.model_info['input_shape'])
        current_layer = inputs
        conv_blocks = []

        # Encoder block
        for i in range(self.model_info['depth']):
            n_filters = self.model_info['n_base_filters']*(2**i)
            conv_block = self.create_conv3d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3, 3), name="convBlock0"+str(i))
            pool_layer = MaxPooling3D(self.model_info['pool_shape'], name="max_pool_"+str(i))(conv_block)
            current_layer = Dropout(self.model_info['dropout']*0.5)(pool_layer)
            conv_blocks.append(conv_block)

        n_filters = self.model_info['n_base_filters']*(2**self.model_info['depth'])
        current_layer = self.create_conv3d_block(current_layer, n_filters=n_filters, kernel_shape=(3, 3, 3))

        # Decoder block
        for i, conv_block in reversed(list(enumerate(conv_blocks))):
            n_filters = self.model_info['n_base_filters']*(2**(i+1))
            deconv_block = self.create_deconv3d_block(current_layer, conv_block, n_filters, (3, 3, 3), strides=self.model_info['pool_shape'], name="deconvBlock"+str(i))
            deconv_block = Dropout(self.model_info['dropout'])(deconv_block)
            current_layer = self.create_conv3d_block(deconv_block, n_filters=n_filters, kernel_shape=(3, 3, 3), name="convBlock1"+str(i))
        p = MaxPooling3D((1, 1, self.model_info['input_shape'][2]), name='max_block_8')(current_layer)
        r = Reshape((self.model_info['input_shape'][0], self.model_info['input_shape'][1], self.model_info['n_base_filters']*2))(p)
        outputs = Conv2D(len(self.model_info['classes']), (1, 1), activation=self.model_info['final_activation'], name="output")(r)

        model.initialize(inputs, outputs)
        if self.save_db:
            model.save_db(self.model_info)
        return model

    def create_conv3d_block(self, input_tensor, n_filters, kernel_shape, activation='relu',
                            name="default"):
        layer = Conv3D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name+'0')(input_tensor)
        if self.model_info['batchnorm']:
            layer = BatchNormalization()(layer)
        layer = Activation(activation)(layer)

        # second layer of the convolutional block
        layer = Conv3D(filters=n_filters, kernel_size=kernel_shape, kernel_initializer="he_normal",
                       padding="same", name=name+'1')(layer)
        if self.model_info['batchnorm']:
            layer = BatchNormalization()(layer)
        return Activation(activation)(layer)

    @staticmethod
    def create_deconv3d_block(input_tensor, conv_block, n_filters, kernel_shape, strides=(2, 2, 2), name="default"):
        up_layer = Conv3DTranspose(n_filters, kernel_size=kernel_shape, strides=strides, padding='same', name=name)(input_tensor)
        return concatenate([up_layer, conv_block])
