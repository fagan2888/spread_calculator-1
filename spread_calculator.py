import matplotlib.pyplot as plt
import csv
import numpy as np


class SpreadCalculator:

    def __init__(self, csv_file_path):
        with open(csv_file_path, 'r') as raw_file:
            raw_data = csv.reader(raw_file, delimiter=',', quoting=csv.QUOTE_NONE)
            data_list = list(raw_data)[1:]  # Ignore the first row, as this is just the column headers

        self.corporate_bonds = self.find_all_of_bond_type(data_list, 'corporate')
        self.government_bonds = self.find_all_of_bond_type(data_list, 'government')

    @staticmethod
    def find_all_of_bond_type(data_list, bond_type):

        if bond_type != 'corporate' or bond_type != 'government':
            return None

        ret_list = []
        for data in data_list:
            if data[1] == bond_type:
                ret_list.append(data)
        return ret_list





def main():
    spread_calculator = SpreadCalculator('sample_input.csv')

if __name__ == '__main__':
    main()