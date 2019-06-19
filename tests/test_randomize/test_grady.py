"""Tests the randomize Grady method module
"""
import numpy as np
import pytest

from lmpy import Matrix
from lmpy.randomize.grady import grady_randomize
from copy import deepcopy


# .............................................................................
class Test_grady_randomize(object):
    """Test the randomize method
    """
    # .....................................
    def _test_pam_randomization(self, pam):
        """Helper function to test randomization
        """
        rand = grady_randomize(deepcopy(pam))
        # Randomize until not the same as original
        count = 10
        while np.all(rand == pam) and count > 0:
            rand = grady_randomize(deepcopy(pam))
            count -= 1
        if count <= 0:
            raise Exception('Randomized PAM is same as original')

        # Test that marginal totals are the same
        assert np.all(np.sum(pam, axis=1) == np.sum(rand, axis=1))
        assert np.all(np.sum(pam, axis=0) == np.sum(rand, axis=0))

    # .....................................
    def test_empty_column(self):
        """Test with a known matrix that has an empty column
        """
        pam = Matrix(
            np.array([
                [0, 1, 0, 1, 0],
                [1, 1, 0, 0, 0],
                [0, 0, 0, 0, 1],
                [1, 1, 0, 1, 1]]))
        self._test_pam_randomization(pam)

    # .....................................
    def test_empty_row(self):
        """Test with a known matrix that has an empty row
        """
        pam = Matrix(
            np.array([
                [0, 1, 0, 1, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
                [1, 1, 0, 1, 1]]))
        self._test_pam_randomization(pam)

    # .....................................
    def test_full_column(self):
        """Test with a known matrix that has a full column
        """
        pam = Matrix(
            np.array([
                [0, 1, 1, 1, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 1, 0, 1],
                [1, 1, 1, 1, 1]]))
        self._test_pam_randomization(pam)

    # .....................................
    def test_full_row(self):
        """Test with a known matrix that has a full row
        """
        pam = Matrix(
            np.array([
                [0, 1, 0, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 1],
                [1, 1, 0, 1, 1]]))
        self._test_pam_randomization(pam)

    # .....................................
    def test_known_matrix(self):
        """Test with a known matrix
        """
        pam = Matrix(
            np.array([
                [0, 1, 0, 1, 0],
                [1, 1, 1, 0, 0],
                [0, 0, 1, 0, 1],
                [1, 1, 0, 1, 1]]))
        self._test_pam_randomization(pam)

    # .....................................
    def test_random_large_matrix(self):
        """Test with a randomly generated large matrix
        """
        pam = Matrix(np.random.randint(0, 2, size=(1000, 10000)))
        self._test_pam_randomization(pam)

    # .....................................
    def test_random_matrix(self):
        """Test with a randomly generated matrix
        """
        pam = Matrix(np.random.randint(0, 2, size=(10, 10)))
        self._test_pam_randomization(pam)
