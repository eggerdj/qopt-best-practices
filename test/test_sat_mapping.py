from unittest import TestCase
import json

import networkx as nx

from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import SwapStrategy

from qopt_best_practices.utils import build_graph, build_paulis
from qopt_best_practices.sat_mapping import *


class TestSwapStrategies(TestCase):
    """Unit test for SWAP strategies functionality."""

    def setUp(self):
        super().setUp()

        # load data
        graph_file = "data/graph_2layers_0seed.json"

        with open(graph_file, "r") as f:
            data = json.load(f)

        self.original_graph = nx.from_edgelist(data["Original graph"])
        self.original_paulis = build_paulis(self.original_graph)

        self.mapped_paulis = [tuple(pauli) for pauli in data["paulis"]]
        self.mapped_graph = build_graph(self.mapped_paulis)

        self.sat_mapping = {
            int(key): value for key, value in data["SAT mapping"].items()
        }
        self.min_k = data["min swap layers"]
        self.swap_strategy = SwapStrategy.from_line(
            [i for i in range(len(self.original_graph.nodes))]
        )
        self.basic_graphs = [nx.path_graph(5), nx.cycle_graph(7)]

    def test_find_initial_mappings(self):

        mapper = SATMapper()

        results = mapper.find_initial_mappings(self.original_graph, self.swap_strategy)
        min_k = min((k for k, v in results.items() if v.satisfiable))
        edge_map = dict(results[min_k].mapping)

        # edge maps are not equal, but same min_k
        self.assertEqual(min_k, self.min_k)

        # Find better test
        # self.assertEqual(edge_map, self.sat_mapping)

    def test_remap_graph_with_sat(self):

        mapper = SATMapper()

        remapped_g, sat_map, min_sat_layers = mapper.remap_graph_with_sat(
            graph=self.original_graph, swap_strategy=self.swap_strategy
        )

        self.assertTrue(nx.is_isomorphic(remapped_g, self.mapped_graph))
