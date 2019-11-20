import ee

LABELS = {
    'corn': 1,
    'soybeans': 5,
    'alfalfa': 36,
    'wheat':  22,
    'forrest': 63,
}

CULTIVATED = {
    'corn': 1,
    'soybeans': 1,
    'alfalfa': 1,
    'wheat':  1,
    'forrest': 2,
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

    def group_labels(self,labels,new_label, tresh):
        check_labels(labels)
        confidence = self.collection.select('confidence').first()
        cultivated = self.collection.select('cultivated').first()
        cropland = self.collection.select('cropland',[new_label]).first()
        crop_mask = cropland.eq(LABELS[labels[0]])
        for label in labels[1:]:
            crop_mask = crop_mask.add(cropland.eq(LABELS[label]))
        return crop_mask.where(confidence.lt(tresh), 0)

    def concatenate_labels(self, labels, thresh):
        check_labels(labels)
        confidence = self.collection.select('confidence').first()
        cultivated = self.collection.select('cultivated').first()
        cropland = self.collection.select('cropland').first()
        crop_mask = [self.collection.select(['cropland'], [label]).first().eq(LABELS[label]).where(confidence.lt(thresh), 0).where(cultivated.eq(CULTIVATED[label]), 0) for label in labels]
        bg = ee.Image(1)
        for mask in crop_mask:
            bg = bg.neq(mask)
        final_mask = crop_mask + [bg.select(['constant'], ['background'])]
        [print(crop.getInfo()) for crop in final_mask]
        return ee.Image.cat(final_mask)

    def conactenate_image(self, images):
        return ee.Image.cat(images)







