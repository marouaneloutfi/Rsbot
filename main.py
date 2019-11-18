from models.unet_3d import Unet3D




input_shape = (128, 128, 8, 8)
unet_3d = Unet3D(input_shape, n_base_filters=16, num_classes=5, dropout=0.25,
               depth=3)

model = unet_3d.get_model()

print(model.summary())