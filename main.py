import random
import folium
import numpy as np
from gee.core import Gee, Landsat8
from gee.crops import Crops
from gee.utils import temp_concatenate
from gee.dataset import Dataset
from models.unet_3d import Unet3D
from gee.tf_io import TfDatasetParser, binary_mask, binary_mask_original
from matplotlib import pyplot as plt
gee = Gee.get_instance(auth=False)


def show_image(image):
    rgb = image[:, :, :3, 0]
    rgb = np.interp(rgb, (rgb.min(), rgb.max()), (0, 255))
    rgb = rgb[..., ::-1]
    rgb = np.array(rgb, np.uint8)
    plt.imshow(rgb)
    plt.show()




# The geographical Area from where to sample our training data
# coordinates are in ESPG:4326
TRAINING_RECTANGLE  = [[-96.7905526395798, 44.12048162104597],
                       [-96.7905526395798, 41.54287486023206],
                       [-92.1323495145798, 41.54287486023206],
                       [-92.1323495145798, 44.12048162104597]]

VALIDATION_RECTANGLE = [[-99.8032479520798, 47.44836764551152],
                        [-99.8032479520798, 42.41202097305778],
                        [-97.2983651395798, 42.41202097305778],
                        [-97.2983651395798, 47.44836764551152]]

# Image size for example 256x256
KERNEL_SIZE = 128

#number of Landsat8 bands to use
#For the pupose of this example "cropland classification", we have chosen to discard
# Band 1,8,9 because they hold little to no information about vegetation cover
# henceforth, the number of bands to use is 8
N_BANDS = 8

# To account for the temporal effect, each sample contains images over a certain period of time
# Generally, in the United States the agriculture season starts from Mars to  October
# For this example, an image is taken for every month, therefore the number of months is 8
N_MONTHS = 8

# landsat = Landsat8('LANDSAT/LC08/C01/T1_SR')
#
# crops = Crops(2017)
#
#
labels = ['corn', 'soybeans', 'alfalfa', 'wheat', 'forrest']
#

input_shape = (KERNEL_SIZE, KERNEL_SIZE, N_BANDS, N_MONTHS)
unet_3d = Unet3D(input_shape, n_base_filters=8, num_classes=5, dropout=0.25,
               depth=3, pool_shape=(2, 2, 2))

model = unet_3d.get_model()

print(model.summary())


model.load_weights('/home/marouane/Downloads/crops_512_8_8_5_focal_softmax_allOneGo.h5')

shard = '/home/marouane/testing/*.tfrecord.gz'
tf_parser = TfDatasetParser(128, labels)
dataset = tf_parser.get_dataset(shard, 128, shuffle=False)

# preds_val = model.predict(dataset, verbose=1, steps=EVAL_B_SIZE)

for i  in range(1):
  example = iter(dataset.take(1)).next()
  myinput = example[0][0].numpy()
  myinput = np.array([myinput])
  rgb = example[0][0].numpy()[:, :,:3, 6]
  r_crops = example[1][0].numpy()
  rgb = np.interp(rgb, (rgb.min(), rgb.max()), (0, 255))
  rgb = rgb[...,::-1]
  rgb = np.array(rgb, np.uint8)
  out_pred = model.predict(myinput)
  pred_crops = binary_mask_original(out_pred[0])
  print(pred_crops.shape)
  crops = binary_mask(r_crops)
  fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
  fig.suptitle('Landsat8 image  and its croptype visualisation')
  ax1.imshow(rgb)
  ax2.imshow(crops)
  ax3.imshow(pred_crops)
  plt.show()