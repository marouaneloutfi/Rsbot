import ee

LABELS = {
    'Corn': 1,
    'Cotton': 2,
    'Rice': 3,
    'Soybeans': 5,
    'Sunflower': 6,
    'Durum Wheat': 22,
    'Spring Wheat': 23,
    'Winter Wheat': 24,
    'Other Small Grains': 25,
    'Alfalfa': 36,
    'Sugarbeets': 41,
    'Dry Beans': 42,
    'Potatoes': 43,
    'Sweet Potatoes': 46,
    'Cucumbers': 50,
    'Forest': 63,
    'Grapes': 69,
    'Developed': 82,
    'Developed/Open Space': 121,
    'Developed/Low Intensity': 122,
    'Developed/Med Intensity': 123,
    'Developed/High Intensity': 124,
    'Deciduous Forest': 141,
    'Evergreen Forest': 142,
    'Mixed Forest': 143,
    'Grassland/Pasture': 176,
    'olives': 211,
    'Dbl Crop Lettuce/Cotton': 232
}

CULTIVATED = {

    'Corn': 1,
    'Cotton': 1,
    'Rice': 1,
    'Soybeans': 1,
    'Sunflower': 1,
    'Durum Wheat': 1,
    'Spring Wheat': 1,
    'Winter Wheat': 1,
    'Other Small Grains': 1,
    'Alfalfa': 1,
    'Sugarbeets': 1,
    'Dry Beans': 1,
    'Potatoes': 1,
    'Sweet Potatoes': 1,
    'Dbl Crop Lettuce/Cotton': 1,
    'Cucumbers': 1,
    'Grapes': 1,
    'Forest': 2,
    'Deciduous Forest': 2,
    'Evergreen Forest': 2,
    'Mixed Forest': 2,
    'Grassland/Pasture': 2,
    'Developed': 2,
    'Developed/Open Space': 2,
    'Developed/Low Intensity': 2,
    'Developed/Med Intensity': 2,
    'Developed/High Intensity': 2,
    'olives': 211
}


def check_labels(labels):
    unknown = [label for label in labels if label not in LABELS.keys()]
    if unknown:
        raise ValueError(' '.join(unknown) + ' : unknown crop types')


class Crops:
    """
    a wrapper for the USDA NASS Cropland Data Layers available at Google earth engine datasets
    """

    uri = 'USDA/NASS/CDL'

    def __init__(self, year):
        year = str(year)
        self.collection = ee.ImageCollection(self.uri).filterDate(year+'-01-01', year+'-12-31')
        print(self.collection.first().getInfo())

    @staticmethod
    def apply_palette(image):
        return image.visualize(bands="cropland")

    def palette(self):
        return self.collection.map(Crops.apply_palette)

    def group_labels(self, labels, new_label, thresh):
        check_labels(labels)
        confidence = self.collection.select('confidence').first()
        cropland = self.collection.select(['cropland']).first()
        crop_mask = self.collection.select(['cropland'], [new_label]).first().eq(LABELS[labels[0]])
        for label in labels[1:]:
            crop_mask = crop_mask.add(cropland.eq(LABELS[label]))
        return crop_mask.where(confidence.lt(thresh), 0)

    def concatenate_labels(self, labels, thresh):
        check_labels(labels)
        confidence = self.collection.select('confidence').first()
        cultivated = self.collection.select('cultivated').first()
        crop_mask = [self.collection.select(['cropland'], [label]).first().eq(LABELS[label]).where(confidence.lt(thresh), 0).where(cultivated.eq(CULTIVATED[label]), 0) for label in labels]
        return ee.Image.cat(crop_mask)

    @staticmethod
    def concatenate_image(images, background=True):
        image = ee.Image.cat(images)
        if background:
            bg = ee.Image(1)
            bands = image.bandNames()
            for i in range(bands.size().getInfo()):
                bg = bg.neq(image.select(bands.get(i).getInfo()))
            image = ee.Image.cat(images + [bg.select(['constant'], ['background'])])
        print(image.getInfo())
        return image
