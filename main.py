from models.unet_3d import Unet3D


input_shape = (256, 256, 3, 8)


unet_3d = Unet3D(input_shape, n_base_filters=16, num_classes=
12, dropout=0.05,
               depth=4, pool_shape=(2, 2, 1))

model = unet_3d.get_model(final_activation="sigmoid")



print(model.summary())