import ee
from .utils import split_rectangle


def create_task(samples, selectors, description, folder):
    """
    Creates a GEE export batch from samples to a TFRecord in Google Drive
    :param samples: a feature collection containing our samples
    :param selectors: the Bands or columns to export
    :param description: the filename of the exported TFRecord in Google Drive
    :param folder: the Google Drive Folder to export into
    :return: None
    """
    return ee.batch.Export.table.toDrive(
        collection=samples,
        description=description,
        folder=folder,
        fileFormat='TFRecord',
        # selectors=selectors
    )


class Dataset:

    def __init__(self, image, bbox, density, export_size=30):
        self.batches = []
        self.current_batch = None
        self.data = image
        self.geom = split_rectangle(ee.Geometry.Polygon(bbox), density[0], density[1])
        self.length = len(self.geom)
        self.exp_size = export_size
        self.counter = 0
        self.size = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter >= self.length:
            raise StopIteration
        else:
            try:
                samples = self.sample_data(self.geom[self.counter: self.counter + self.exp_size])
                self.counter += self.exp_size
                return samples
            except IndexError:
                samples = self.sample_data(self.geom[self.counter:])
                self.counter += self.exp_size
                return samples

    def sample_data(self, geom):
        geom_sample = ee.FeatureCollection([])
        for g in geom:
            sample = self.data.sample(
                region=g,
                scale=30,
                numPixels=10,
                seed=42,
                # dropNulls=True
            )
            geom_sample = geom_sample.merge(sample)
        self.size += geom_sample.size().getInfo()
        return geom_sample

    def export_to_drive(self, geom_sample, selectors, desc, folder='records'):
        self.current_batch = create_task(geom_sample, selectors, desc, folder)
        self.current_batch.start()
        self.batches.append(self.current_batch)
        return self.current_batch
