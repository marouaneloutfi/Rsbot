import ee


def init_gee():
    return Gee.get_instance()


class Gee:

    __instance = None
    tiles = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'

    @staticmethod
    def get_instance(ipython=False):
        if Gee.__instance is None:
            Gee(ipython)
        return Gee.__instance

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(Gee)
        return cls.__instance

    def __init__(self, oauth=False):
        if oauth:
            ee.Authenticate()
        ee.Initialize()


class Satellite:

    bands = []

    def __init__(self, uri):
        self.collection = ee.ImageCollection(uri)

    def filter_date(self, start_date, end_date):
        self.collection = self.collection.filterDate(start_date, end_date)

    def filter_bounds(self, geom):
        self.collection = self.collection.filterBounds(geom)

    def set_bands(self, bands):
        self.bands = bands


class Landsat8(Satellite):

    optical_bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
    thermal_bands = ['B10', 'B11']

    def __init__(self, uri):
        super().__init__(uri)
        self.set_bands(self.optical_bands + self.thermal_bands)

    """ 
    Function to mask clouds based on the pixel_qa band of Landsat 8 SR data.
    @param {ee.Image} image Input Landsat 8 SR image
    @return {ee.Image} Cloud masked Landsat 8 image
    @source  https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T2_SR   
    """
    def mask_l8sr(self, image):
        cloud_shadow_bit_mask = ee.Number(2).pow(3).int()
        clouds_bit_mask = ee.Number(2).pow(5).int()
        qa = image.select('pixel_qa')
        mask1 = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0).And(
            qa.bitwiseAnd(clouds_bit_mask).eq(0))
        mask2 = image.mask().reduce('min')
        mask3 = image.select(self.optical_bands).gt(0).And(
            image.select(self.optical_bands).lt(10000)).reduce('min')
        mask = mask1.And(mask2).And(mask3)
        return image.select(self.optical_bands).divide(10000).addBands(
            image.select(self.thermal_bands).divide(10).clamp(273.15, 373.15)
                    .subtract(273.15).divide(100)).updateMask(mask)

    def filter_clouds(self, collection):
        return collection.map(self.mask_l8sr)
