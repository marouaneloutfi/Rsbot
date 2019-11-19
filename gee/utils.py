import numpy as np
import ee


def split_rectangle(rect, x_density, y_density, geometry='polygon'):
    """
    divide a rectangular shape Polygon into a grid of polygons or points
    @:param {ee.Geometry.Polygon}
    @:param {float:x_density} grid's density along the x axis
    @:param {float:y_density} grid's density along the y axis
    @:param {string:geometry} output type: 'point' or 'polygon' default to polygon
    @:returns {[ee.Geometry]} a list of earth engine points or polygon
    """
    coords = rect['coordinates'][0]
    min_x, max_x = coords[0][0], coords[2][0]
    min_y, max_y = coords[1][1], coords[0][1]
    x = np.arange(min_x, max_x, x_density)
    y = np.arange(min_y, max_y, y_density)
    if geometry == 'polygon':
        return [ee.Geometry.Polygon([[[_x, _y + y_density],
                                      [_x, _y],
                                      [_x + x_density, _y],
                                      [_x + x_density, _y + y_density]]]) for _x in x for _y in y]
    elif geometry == 'point':
        points = []
        for _x in x:
            for _y in y:
                points.append(ee.Geometry.Point([_x, _y + y_density]))
                points.append(ee.Geometry.Point([_x, _y]))
                points.append(ee.Geometry.Point([_x + x_density, _y]))
                points.append(ee.Geometry.Point([_x + x_density, _y + y_density]))
        return points
    else:
        raise ValueError("geometry type not supported yet")


def join_collection(image, mask):
    join = ee.Join.inner()
    time_filter = ee.Filter.equals(leftField='system:time_start',
                                   rightField='system:time_start')
    return join.apply(image, mask, time_filter)


def ee_concatenate(feature):
    return ee.Image.cat(feature.get('primary'), feature.get('secondary'))


def temp_divide(bands, month):
    return [band+'-'+str(month) for band in bands]


def get_selectors(bands):
    selectors = []
    for month in range(3, 11):
        selectors += temp_divide(bands, month)
    return selectors


def temp_concatenate(satellite, labels, year, kernel_size=256,  sr=True):
    year = str(year)
    img_c = satellite.collection.sort('system:time_start')
    img_m = img_c.filterDate(year + '-03-01', year + '-03-30')

    if sr:
        img_m = satellite.filter_clouds(img_m)

    img_m = img_m.select(satellite.bands, temp_divide(satellite.bands, 3)).median()
    for month in range(3, 11):
        if month >= 10:
            datefilter = ee.Filter.date(year + '-' + str(month) + '-01',
                                        year + '-' + str(month) + '-30')
        else:
            datefilter = ee.Filter.date(year + '-0' + str(month) + '-01',
                                        year + '-0' + str(month) + '-30')
        current_img = img_c.filter(datefilter)
        if sr:
            current_img = satellite.filter_clouds(current_img)

        current_img = current_img.select(satellite.bands, temp_divide(satellite.bands, month)).median()
        img_m = ee.Image.cat([img_m, current_img])

    feature_stack = ee.Image.cat([img_m, labels]).float()
    _list = ee.List.repeat(1, kernel_size)
    lists = ee.List.repeat(_list, kernel_size)
    kernel = ee.Kernel.fixed(kernel_size, kernel_size, lists)
    return feature_stack.neighborhoodToArray(kernel)
