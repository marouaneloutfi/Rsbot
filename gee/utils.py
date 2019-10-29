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
