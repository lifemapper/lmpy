"""Tests the occurrence_transformation module."""
from copy import deepcopy
from operator import itemgetter
import os
from random import randint, shuffle
import tempfile

import numpy as np
import pytest

from lmpy import Point
from lmpy.point import (
    convert_delimited_to_point, convert_json_to_point, none_getter)
from lmpy.data_wrangling.occurrence.modifiers import (
    get_coordinate_converter_modifier)


# .............................................................................
def _flag_getter(index):
    """Returns a getter for the test flags separated by ', '"""
    def getter(obj):
        flag_string = obj[index]
        return flag_string.split(', ')
    return getter


# .............................................................................
def test_none_getter():
    """Tests that none_getter always returns None."""
    getter = none_getter
    assert getter(0) is None
    assert getter('a') is None
    assert getter(None) is None
    assert getter(b'0000') is None


# .............................................................................
class Test_convert_delimited_to_point:
    """Tests the convert_delimited_to_point function."""
    # ..........................
    def _check_points(self, points):
        """Check that the points look okay."""
        for point in points:
            assert isinstance(point, Point)
            assert isinstance(point.species_name, str)
            assert isinstance(point.x, (int, float))
            assert -180.0 <= point.x <= 180.0
            assert isinstance(point.y, (int, float))
            assert -90.0 <= point.y <= 90.0
            assert isinstance(point.flags, list)

    # ..........................
    def _create_delimited_file(self, delimiter, header=True):
        """Create a file for testing."""
        filename = tempfile.NamedTemporaryFile().name
        num_points = randint(0, 20)

        # Randomize field order
        headers = ['species', 'longitude', 'latitude', 'flags']
        field_order = [0, 1, 2, 3]
        shuffle(field_order)
        # Create file
        with open(filename, mode='w', encoding='utf8') as out_file:
            # Write header if desired
            if header:
                reordered_headers = [
                    headers[field_order[0]], headers[field_order[1]],
                    headers[field_order[2]], headers[field_order[3]]]
                out_file.write('{}'.format(delimiter).join(reordered_headers))
                out_file.write('\n')
            for i in range(num_points):
                values = ['"species A"', str(randint(-180, 180)),
                          str(randint(-90, 90)), '"{}"'.format(
                              ', '.join(
                                  ['flag {}'.format(i) for i in range(
                                      randint(0, 10))]))]
                reordered_values = [
                    values[field_order[0]], values[field_order[1]],
                    values[field_order[2]], values[field_order[3]]]
                out_file.write('{}'.format(delimiter).join(reordered_values))
                out_file.write('\n')
        # Return field order
        return (filename,
                (field_order.index(0), field_order.index(1),
                 field_order.index(2), field_order.index(3)))

    # ..........................
    def test_int_getters_comma_headers(self):
        """Test using field index integers, comma delimiters, and header."""
        filename, field_order = self._create_delimited_file(',', header=True)
        try:
            points = convert_delimited_to_point(
                filename, field_order[0], field_order[1], field_order[2],
                flags_getter=_flag_getter(field_order[3]), delimiter=',',
                headers=True)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_getters_comma_headers(self):
        """Test using field getters, comma delimiters, and header."""
        filename, field_order = self._create_delimited_file(',', header=True)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(field_order[1])
        y_getter = itemgetter(field_order[2])
        flags_getter = _flag_getter(field_order[3])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                flags_getter=flags_getter, delimiter=',', headers=True)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_int_getters_comma_no_headers(self):
        """Test using field index integers, comma delimiters, and no header."""
        filename, field_order = self._create_delimited_file(',', header=False)
        try:
            points = convert_delimited_to_point(
                filename, field_order[0], field_order[1], field_order[2],
                flags_getter=_flag_getter(field_order[3]), delimiter=',',
                headers=False)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_getters_comma_no_headers(self):
        """Test using field getters, comma delimiters, and no header."""
        filename, field_order = self._create_delimited_file(',', header=False)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(field_order[1])
        y_getter = itemgetter(field_order[2])
        flags_getter = _flag_getter(field_order[3])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                flags_getter=flags_getter, delimiter=',', headers=False)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_int_getters_tab_headers(self):
        """Test using field index integers, tab delimiters, and header."""
        filename, field_order = self._create_delimited_file('\t', header=True)
        try:
            points = convert_delimited_to_point(
                filename, field_order[0], field_order[1], field_order[2],
                flags_getter=_flag_getter(field_order[3]), delimiter='\t',
                headers=True)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_getters_tab_headers(self):
        """Test using field getters, tab delimiters, and header."""
        filename, field_order = self._create_delimited_file('\t', header=True)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(field_order[1])
        y_getter = itemgetter(field_order[2])
        flags_getter = _flag_getter(field_order[3])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                flags_getter=flags_getter, delimiter='\t', headers=True)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_int_getters_tab_no_headers(self):
        """Test using field index integers, tab delimiters, and no header."""
        filename, field_order = self._create_delimited_file('\t', header=False)
        try:
            points = convert_delimited_to_point(
                filename, field_order[0], field_order[1], field_order[2],
                flags_getter=_flag_getter(field_order[3]), delimiter='\t',
                headers=False)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_getters_tab_no_headers(self):
        """Test using field getters, tab delimiters, and no header."""
        filename, field_order = self._create_delimited_file('\t', header=False)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(field_order[1])
        y_getter = itemgetter(field_order[2])
        flags_getter = _flag_getter(field_order[3])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                flags_getter=flags_getter, delimiter='\t', headers=False)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_no_flags(self):
        """Test when no flags are pulled."""
        filename, field_order = self._create_delimited_file(',', header=True)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(field_order[1])
        y_getter = itemgetter(field_order[2])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                delimiter=',', headers=True)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)

    # ..........................
    def test_bad_index(self):
        """Test with bad index for getter."""
        filename, field_order = self._create_delimited_file('\t', header=False)
        species_getter = itemgetter(field_order[0])
        x_getter = itemgetter(999)
        y_getter = itemgetter(field_order[2])
        flags_getter = _flag_getter(field_order[3])
        try:
            points = convert_delimited_to_point(
                filename, species_getter, x_getter, y_getter,
                flags_getter=flags_getter, delimiter='\t', headers=False)
            self._check_points(points)
        except Exception as err:
            raise err
        finally:
            os.remove(filename)


# .............................................................................
class Test_convert_json_to_point:
    """Tests the convert_json_to_point function."""
    # ..........................
    def _check_points(self, points):
        """Check that the points look okay."""
        for point in points:
            assert isinstance(point, Point)
            assert isinstance(point.species_name, str)
            assert isinstance(point.x, (int, float))
            assert -180.0 <= point.x <= 180.0
            assert isinstance(point.y, (int, float))
            assert -90.0 <= point.y <= 90.0
            assert isinstance(point.get_attribute('flags'), list)

    # ..........................
    def test_simple(self):
        """Perform a simple test of easy json."""
        json_obj = [
            {'species': 'species A',
             'x': randint(-180, 180),
             'y': randint(-90, 90),
             'flags': ', '.join(
                 ['flag {}'.format(i) for i in range(randint(0, 10))])
             } for i in range(randint(0, 10))
            ]
        points = convert_json_to_point(
            json_obj, itemgetter('species'), itemgetter('x'), itemgetter('y'),
            _flag_getter('flags'))
        self._check_points(points)

    # ..........................
    def test_simple_no_flags(self):
        """Perform a simple test of easy json with no flags."""
        json_obj = [
            {'species': 'species A',
             'x': randint(-180, 180),
             'y': randint(-90, 90)
             } for i in range(randint(0, 10))
            ]
        points = convert_json_to_point(
            json_obj, itemgetter('species'), itemgetter('x'), itemgetter('y'))
        self._check_points(points)

    # ..........................
    def test_nested(self):
        """Perform a simple test of easy json."""
        json_obj = {
            'something': 'a value',
            'points': [
                {'species': 'species A',
                 'x': randint(-180, 180),
                 'y': randint(-90, 90),
                 'flags': ', '.join(
                     ['flag {}'.format(i) for i in range(randint(0, 10))])
                 } for i in range(randint(0, 10))
                ]
            }
        points = convert_json_to_point(
            json_obj, itemgetter('species'), itemgetter('x'), itemgetter('y'),
            _flag_getter('flags'), point_iterator=itemgetter('points'))
        self._check_points(points)

    # ..........................
    def test_nested_no_flags(self):
        """Perform a simple test of easy json with no flags."""
        json_obj = {
            'something': 'a value',
            'points': [
                {'species': 'species A',
                 'x': randint(-180, 180),
                 'y': randint(-90, 90)
                 } for i in range(randint(0, 10))
                ]
            }
        points = convert_json_to_point(
            json_obj, itemgetter('species'), itemgetter('x'), itemgetter('y'),
            point_iterator=itemgetter('points'))
        self._check_points(points)


# .............................................................................
class Test_get_coordinate_converter:
    """Test get_coordinate_converter."""
    # ..........................
    def test_specific_values(self):
        """Test that conversion produces known values."""
        in_vals = (4326, -89.555857, 37.3040553)
        out_vals = (2815, 333699.36, 163612.51)
        converter = get_coordinate_converter_modifier(in_vals[0], out_vals[0])
        in_point = Point('test species', in_vals[1], in_vals[2])
        out_point = converter(in_point)
        assert np.isclose(out_point.x, out_vals[1])
        assert np.isclose(out_point.y, out_vals[2])
        assert in_point.species_name == out_point.species_name

    # ..........................
    def test_to_and_back(self):
        """Test conversion from one to another and back."""
        in_vals = (4326, -89.555857, 37.3040553)
        converter = get_coordinate_converter(in_vals[0], 3395)
        converter_2 = get_coordinate_converter(3395, in_vals[0])
        in_point = Point('test species', in_vals[1], in_vals[2])
        out_point = converter(in_point)
        out_point_2 = converter_2(out_point)
        assert np.isclose(out_point_2.x, in_vals[1])
        assert np.isclose(out_point_2.y, in_vals[2])
        assert in_point.species_name == out_point.species_name

    # ..........................
    def test_transitive(self):
        """Test conversion from one to another to another and back."""
        in_vals = (4326, -89.555857, 37.3040553)
        epsgs = [3395, 2815]
        original_point = Point('Test species', in_vals[1], in_vals[2])
        in_point = deepcopy(original_point)
        src_epsg = in_vals[0]
        for target_epsg in epsgs:
            converter = get_coordinate_converter(src_epsg, target_epsg)
            in_point = converter(in_point)
            src_epsg = target_epsg
        final_converter = get_coordinate_converter(src_epsg, in_vals[0])
        final_point = final_converter(in_point)
        assert np.isclose(final_point.x, original_point.x)
        assert np.isclose(final_point.y, original_point.y)
        assert final_point.species_name == original_point.species_name
