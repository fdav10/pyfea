"""Test properties of elements.

Reference values are mostly taken from 'Introduction to Finite Element
Methods' by Carlos A Felippa."""

import pytest

import numpy as np

from pyfea.fea import FeModel
from pyfea.elements import Node, Bar


np.set_printoptions(precision=2, suppress=True)


nodes = [Node([0, 0], 0),
         Node([10, 0], 1),
         Node([10, 10], 2)]

node_pairs = [(nodes[0], nodes[1]),
              (nodes[1], nodes[2]),
              (nodes[0], nodes[2])]

forces = [0, 0, 0, 0, 2, 1]
displacements = [0, 0, None, 0, None, None]

reference_ks = [
    [[1, 0, -1, 0],
     [0, 0, 0, 0],
     [-1, 0, 1, 0],
     [0, 0, 0, 0]],
    [[0, 0, 0, 0],
     [0, 1, 0, -1],
     [0, 0, 0, 0],
     [0, -1, 0, 1]],
    [[0.5, 0.5, -0.5, -0.5],
     [0.5, 0.5, -0.5, -0.5],
     [-0.5, -0.5, 0.5, 0.5],
     [-0.5, -0.5, 0.5, 0.5]]
]

reference_global_k = [[20, 10, -10, 0, -10, -10],
                      [10, 10, 0, 0, -10, -10],
                      [-10, 0, 10, 0, 0, 0],
                      [0, 0, 0, 5, 0, -5],
                      [-10, -10, 0, 0, 10, 10],
                      [-10, -10, 0, -5, 10, 15]]

axial_stiffnesses = [100, 50, 200 * 2 ** 0.5]


@pytest.mark.parametrize("node_pair, reference", zip(node_pairs, reference_ks))
def test_bar_global_stiffness_matrix(node_pair, reference):
    bar = Bar(*node_pair, diameter=1)
    k_coefficients = bar.global_stiffness_matrix() / bar.axial_rigidity
    np.testing.assert_array_almost_equal(k_coefficients, reference)


def test_global_stiffness_matrix(fe_model):
    np.testing.assert_array_almost_equal(fe_model.k, reference_global_k)


def test_reduced_displacements(solved_fe_model):
    np.testing.assert_array_almost_equal(solved_fe_model.reduced_u, [0, 0.4, -0.2])


def test_complete_displacements(solved_fe_model):
    np.testing.assert_array_almost_equal(solved_fe_model.displacements, [0, 0, 0, 0, 0.4, -0.2])


@pytest.fixture(scope='module')
def fe_model():
    elements = [Bar(*node_pair, 0) for node_pair in node_pairs]
    for element, k in zip(elements, axial_stiffnesses):
        element.axial_rigidity = k / element.length
    return FeModel(nodes, elements, forces, displacements)


@pytest.fixture(scope='module')
def solved_fe_model(fe_model):
    fe_model.solve()
    return fe_model
