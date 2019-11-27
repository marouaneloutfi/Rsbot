# Welcome to Rsbot Documentation

### Connect to Google Earth engine

The module provides a wrapper class **Gee** for general Google earth engine functions such as initialisation and authentication.

The class is a singleton and can be instantiated the regular way or through the _get_instance_ method:
     
        from Rsbot.gee.core import gee
        gee = Gee.get_instance(auth=True)

If the parameter auth is set to true, You will be directed to a Google Earth Engine web page for an OAuth Authorization token
which you need to paste back in order to continue.
        
## Access Satellite imagery
Two satellite sources are predefined in the module, each of which can be accessed through a class with a proper URI to a
corresponding dataset in G. Earth Engine

        from Rsbot.gee.core import Landsat8, Sentinel2

* Landsat 8
       
        landsat = Landsat8('LANDSAT/LC08/C01/T1_SR')
       
* Sentinel 2
        
        sentinel = Sentinel2('COPERNICUS/S2')

The class Variable _collection_ is what holds the satellite data and is of type _EE.ImageCollection_ 

        > type(landsat.collection)      
          EE.ImageCollection
        
Multiple class methods are available to  filter through the collection of satellite images:
    
* Filter between two dates
        
        landsat.filter_date('2017-01-01', '2017-12-31')
        
* Filter bands
        
        #keep only The RGB bands
        landsat.filter_bands(['B2', 'B3', 'B4'])
* Filter clouds

        landsat.filter_clouds()
        
## Access other raster datasets

For now Rsbot provides access to one Raster GEE Dataset which is  the [USDA](https://developers.google.com/earth-engine/datasets/catalog/USDA_NASS_CDL) NASS Cropland Data Layers.

This Data layer describes for each year  the crop-specific land cover of the entire country of  United States.

        from Rsbot.gee.crops import Crops
        crops = Crops(2017)

The Crops class comes predefined with methods to facilitate the filtering, transformation and handling of the Crops Data Layer

The USDA Cropland dataset comes with 254 predefined crop types. to filter through these types, we use the method _filter_labels_

        labels = ['Corn', 'Soybeans', 'Alfalfa', 'Wheat', 'Forrest']
        crops_labels = crops.filter_labels(labels, thresh=0.85)
        
 The function returns an image containing only the user specified labels with the rest set to zero
 
concatenate_image is a Crop class method to concatenate all the bands in a list of images into one EE image
The parameter background can be set to True to add a band at the end of the image with positive pixel values where every other bands is null.

    fruits = crops.filter_labels(['Apples', 'Oranges'])
    vegetebales = crops.filter_labels(['Potatoes', 'Carrots']
    
    crop_labels = crops.concatenate_image([fruits, vegetables], background=True)

   
## Join two GEE datasets
the Function temp_concatenate in **_gee.utils_** encapsulates the concatenation of satellite images over a period of months
(a median image is taken for each month) and couple them with another raster dataset.
The current implementation works over a period of 8 months from Mars --> October
The result is an EE image with a number of bands equal to the original number multiplied by the number of months plus the labels_image
 
Such function is essential to study the temporal changes in satellite imagery

     temporal_image = temp_concatenate(landsat, crops_labels, year=2017, kernel_size=256)
     
The kernel_size specifies the size of the images to sample later.

## sample a GEE image over a geographical region
First, we need to create a Dataset instance using our EE image.
    
    from Rsbot.gee.dataset import Dataset
    
    dataset = Dataset(temporal_image, TRAINING_RECTANGLE, density=(0.5, 0.5), export_size=30)
    
Where TRAINING_RECTANGLE is a list containing the geographical coordinates of the region
    
        TRAINING_RECTANGLE = [[-84, 44], [-84, 42], [-82, 42], [82, 44]]
        
density is a measure of how close to each other the samples are, the smaller it is, the higher our number of samples,
and the export size is how much samples per batch (number of samples in a single TFrecord)

Once you instantiate a dataset, it can be exported to the corresponding Google Drive account in the following manner:

        for i, samples in  enumerate(iter(dataset)):
    dataset.export_to_drive(samples, '', 'tf_shard_'+str(i), folder="dataset_example")
    
The export of the dataset is done asynchronously, but nonetheless you can check the status of each batch by access the dataset variable
batches:

        for batch in dataset.batches:
            print(batch.status())
   
## train  a Deep Learning  Model

When all of the dataset is exported to Google Drive, we can use them to train pre-defined models in the Rsbot module

Only 2 models are implemented so far, both are based on the Ecoder-decoder Unet archtitecture for sematic segmentation

We initialize our Neural Network Model UNET 3D.

        from rsbot.models.unet_3d import Unet3D
        
        unet_3d = Unet3D((256,256,8,8), n_base_filters=8, num_classes=6, dropout=0.05,
               depth=3, pool_shape=(2, 2, 2))

        model = unet_3d.get_model(final_activation="sigmoid")
 
        
## Visualize results

Some visualisation functions have been added to the module
The following is binairy_mask for rendering segmentation images
        
        from tools.visualize import binary_mask
        prediction = model.predict(myinput)
        prediction_mask = binary_mask(prediction)

also functions to read images and save masks as pngs are available

        from tools.visulize import read_png, save_as_png
        
        image = read_png('example_image.png')
        
        save_as_png(prediction_mask, 'mask_predicted.png')
        
                     