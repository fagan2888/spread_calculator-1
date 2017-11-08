import unittest
from spread_calculator import SpreadCalculator


class SpreadCalculatorTest(unittest.TestCase):

    def setUp(self):
        self.spread_calculator = SpreadCalculator()

    def tearDown(self):
        self.spread_calculator = None

    def test_find_all_bond_type(self):
        input_marix = [['C1', 'corporate', '30 years', '1.5%'], ['G1', 'government', '30 years', '1.5%']]

        corp = self.spread_calculator.find_all_of_bond_type(input_marix, 'corporate')
        gov = self.spread_calculator.find_all_of_bond_type(input_marix, 'government')

        self.assertEqual([['C1', 'corporate', '30 years', '1.5%']], corp)
        self.assertEqual([['G1', 'government', '30 years', '1.5%']], gov)

        none = self.spread_calculator.find_all_of_bond_type(input_marix, 'fail')
        self.assertEqual(none, None)

    def test_read_from_csv(self):
        self.spread_calculator.read_from_csv('test.csv')
        self.assertEqual([['C1', 'corporate', 1.3, 3.3], ['C2', 'corporate', 2.0, 3.8]],
                         self.spread_calculator.corporate_bonds)
        self.assertEqual([['G1', 'government', 0.9, 1.7], ['G2', 'government', 2.3, 2.3],
                          ['G3', 'government', 3.6, 4.5]],
                         self.spread_calculator.government_bonds)

    def test_read_from_data_list(self):
        data_list = [['C1', 'corporate', 30, 1.5], ['G1', 'government', 3.6, 4.5]]
        self.spread_calculator.read_from_data_list(data_list)
        self.assertEqual(self.spread_calculator.corporate_bonds[0], ['C1', 'corporate', 30, 1.5])
        self.assertEqual(self.spread_calculator.government_bonds[0], ['G1', 'government', 3.6, 4.5])

    def test_clean_numeric_values(self):
        data_list = [['C1', 'corporate', '30 years', '1.5%'], ['G1', 'government', '3.6 years', '4.5%']]
        new_data_list = self.spread_calculator.clean_numeric_values(data_list)

        self.assertEqual(new_data_list[0], ['C1', 'corporate', 30, 1.5])
        self.assertEqual(new_data_list[1], ['G1', 'government', 3.6, 4.5])

    def test_nearest_binary_search(self):
        self.spread_calculator.read_from_csv('test.csv')

        best_gov_bond, low, high = self.spread_calculator.nearest_binary_search(self.spread_calculator.government_bonds,
                                                                                2.5)
        self.assertEqual(best_gov_bond, ['G2', 'government', 2.3, 2.30])
        self.assertEqual(low, 1)
        self.assertEqual(high, 2)

        best_gov_bond, low, high = self.spread_calculator.nearest_binary_search(self.spread_calculator.government_bonds,
                                                                                2.1)
        self.assertEqual(best_gov_bond, ['G2', 'government', 2.3, 2.30])
        self.assertEqual(low, 0)
        self.assertEqual(high, 1)

        best_gov_bond, low, high = self.spread_calculator.nearest_binary_search(self.spread_calculator.government_bonds,
                                                                                2.3)
        self.assertEqual(best_gov_bond, ['G2', 'government', 2.3, 2.30])
        self.assertEqual(low, 0)
        self.assertEqual(high, 1)

        # Test the situation where the value is less than the first element's term
        best_gov_bond, low, high = self.spread_calculator.nearest_binary_search(self.spread_calculator.government_bonds,
                                                                                0.8)
        self.assertEqual(best_gov_bond, ['G1', 'government', 0.90, 1.70])
        self.assertEqual(low, 0)
        self.assertEqual(high, 1)

        # Test the situation where the value is greater than the last element's term
        best_gov_bond, low, high = self.spread_calculator.nearest_binary_search(self.spread_calculator.government_bonds,
                                                                                3.8)
        self.assertEqual(best_gov_bond, ['G3', 'government', 3.60, 4.50])
        self.assertEqual(low, 1)
        self.assertEqual(high, 2)

    def test_find_equation_of_line_from_two_points(self):
        points = [(2, 8), (-1, -1)]
        m, b = self.spread_calculator.find_equation_of_line_from_two_points(points)
        self.assertEqual(m, 3)
        self.assertEqual(b, 2)

    def test_calculate_spread_to_curve(self):
        self.spread_calculator.read_from_csv('test.csv')

        result_string = self.spread_calculator.calculate_yield_spread()
        self.assertEqual(result_string, "bond,benchmark,spread_to_benchmark\n"
                                        "C1,G1,1.60%\n"
                                        "C2,G2,1.50%\n")

    def test_calculate_yield_spread(self):
        self.spread_calculator.read_from_csv('test.csv')

        m, b = self.spread_calculator.find_equation_of_line_from_two_points([(0.9, 1.7), (2.3, 2.3)])
        c1_point_on_line = m * self.spread_calculator.corporate_bonds[0][2] + b
        c2_point_on_line = m * self.spread_calculator.corporate_bonds[1][2] + b

        c1_spread = self.spread_calculator.corporate_bonds[0][3] - c1_point_on_line
        c2_spread = self.spread_calculator.corporate_bonds[1][3] - c2_point_on_line

        result_string = self.spread_calculator.calculate_spread_to_curve()
        self.assertEqual(result_string, "bond,spread_to_curve\n" +
                                        "C1,{:.2f}%\n".format(c1_spread) +
                                        "C2,{:.2f}%\n".format(c2_spread))

