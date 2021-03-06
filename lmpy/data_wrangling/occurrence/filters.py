"""Module containing occurrence data wranglers for filtering points."""
from osgeo import ogr
from lmpy.data_wrangling.occurrence.common import (
    get_occurrence_filter, make_list)
from lmpy.spatial import SpatialIndex


# .............................................................................
def get_attribute_filter(att_name, pass_condition):
    """Get a filter function for checking a point attribute.

    Args:
        att_name (str): The attribute of a point to check.
        pass_condition (func): A function that takes a value and returns a
            boolean indicating if it passes a condition.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    # .......................
    def point_filter_func(point):
        """Get the specified attribute from the point and check it."""
        return pass_condition(point.get_attribute(att_name))

    return get_occurrence_filter(point_filter_func)


# .............................................................................
def get_bounding_box_filter(min_x, min_y, max_x, max_y):
    """Get a filter function for the specified bounding box.

    Args:
        x_index (str or int): The index of the 'x' value for each point.
        y_index (str or int): The index of the 'y' value for each point.
        min_x (numeric): The minimum 'x' value for the bounding box.
        min_y (numeric): The minimum 'y' value for the bounding box.
        max_x (numeric): The maximum 'x' value for the bounding box.
        max_y (numeric): The maximum 'y' value for the bounding box.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    # .......................
    def bbox_filter_func(point):
        """Filter for single point."""
        return min_x <= point.x <= max_x and min_y <= point.y <= max_y

    return get_occurrence_filter(bbox_filter_func)


# .............................................................................
def get_decimal_precision_filter(decimal_places):
    """Get a filter function to remove points with inadequate precision.

    Args:
        decimal_places (int): Only keep points with at least this many decimal
            places of precision.
    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    # .......................
    def decimal_precision_filter_func(point):
        """Filter for single point."""
        lat_str = str(point.y)
        lon_str = str(point.x)
        try:
            lat_decimals = len(lat_str) - lat_str.index('.') - 1
            lon_decimals = len(lon_str) - lon_str.index('.') - 1
        except ValueError:
            # TODO: Handle numbers with 'e' example: 1e-05
            return False
        return min([lat_decimals, lon_decimals]) >= decimal_places

    return get_occurrence_filter(decimal_precision_filter_func)


# .............................................................................
def get_disjoint_geometries_filter(geometry_wkts):
    """Get a filter function for finding disjoint geometries.

    Args:
        geometry_wkts (list of str): A list of geometry Well-Known Text strings
            to check for intersection.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    geometries = []
    for wkt in geometry_wkts:
        geometries.append(ogr.CreateGeometryFromWkt(wkt))

    # .......................
    def disjoint_geometry_filter(point):
        """Disjoint geometry filter function."""
        point_geometry = ogr.Geometry(ogr.wkbPoint)
        point_geometry.AddPoint(point.x, point.y)
        return all(
            [geom.Intersection(
                point_geometry).IsEmpty() for geom in geometries])
    return get_occurrence_filter(disjoint_geometry_filter)


# .............................................................................
def get_intersect_geometries_filter(geometry_wkts):
    """Get a filter function for intersecting the provided geometries.

    Args:
        geometry_wkts (list of str): A list of geometry Well-Known Text strings
            to check for intersection.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    geometries = []
    for wkt in geometry_wkts:
        geometries.append(ogr.CreateGeometryFromWkt(wkt))

    # .......................
    def intersect_geometry_filter(point):
        """Intersect geometry filter function."""
        point_geometry = ogr.Geometry(ogr.wkbPoint)
        point_geometry.AddPoint(point.x, point.y)
        return any(
            [not geom.Intersection(
                point_geometry).IsEmpty() for geom in geometries])

    return get_occurrence_filter(intersect_geometry_filter)


# .............................................................................
def get_minimum_points_filter(minimum_count):
    """Get a filter that returns all points if a minimum number, else none.

    Args:
        minimum_count (int): The minimum number of points in order to keep.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    # .......................
    def min_points_filter(points):
        if len(make_list(points)) >= minimum_count:
            return points
        return []

    return min_points_filter


# .............................................................................
def get_spatial_index_filter(spatial_index, get_species_intersections_func,
                             check_hit_func):
    """Get a filter that uses a spatial index and logic to intersect hits.

    Args:
        spatial_index (str or SpatialIndex): A spatial index or file path for
            one to load.
        get_species_intersections_func (method): A method for retrieving valid
            intersections for a species point.
        check_hit_func (method): A method for checking a hit against the valid
            hits for a species point.
    """
    # Load spatial index
    if not isinstance(spatial_index, SpatialIndex):
        spatial_index = SpatialIndex(spatial_index)
    # Store valid intersections for each encountered species
    valid_intersections = {}

    # .......................
    def spatial_index_point_filter(point):
        """Check a point against the spatial index."""
        if point.species_name in valid_intersections:
            check_intersections = valid_intersections[point.species_name]
        else:
            check_intersections = get_species_intersections_func(
                point.species_name)
            valid_intersections[point.species_name] = check_intersections
        if check_intersections is None or len(check_intersections) == 0:
            return True
        for hit in spatial_index.search(point.x, point.y).values():
            if check_hit_func(hit, check_intersections):
                return True
        return False

    return get_occurrence_filter(spatial_index_point_filter)


# .............................................................................
def get_unique_localities_filter():
    """Get a filter that only retains points with unique localities.

    Note:
        Retains the first point with an unseen locality, drops the rest.

    Returns:
        function - A function that takes a list of points as input and returns
            a list of points that pass that filter function.
    """
    unique_localities = []

    # .......................
    def unique_localities_filter(point):
        """Unique localities filter function."""
        test_val = (point.x, point.y)
        if test_val in unique_localities:
            return False
        unique_localities.append(test_val)
        return True

    return get_occurrence_filter(unique_localities_filter)
