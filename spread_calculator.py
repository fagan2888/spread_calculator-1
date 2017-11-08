import csv


class SpreadCalculator:

    def __init__(self):
        self.corporate_bonds = None
        self.government_bonds = None

    """"
        Constructor for creating the spread calculator out of a csv file
        :param csv_file_path: Specifies a relative path for a csv file
    """
    def read_from_csv(self, csv_file_path):
        with open(csv_file_path, 'r') as raw_file:
            raw_data = csv.reader(raw_file, delimiter=',', quoting=csv.QUOTE_NONE)
            data_list = list(raw_data)[1:]  # Ignore the first row, as this is just the column headers

        data_list = self.clean_numeric_values(data_list)
        self.read_from_data_list(data_list)


    """"
        Constructor for creating the spread calculator out of an already created data list.
        Primarily used for testing purporses.
        :param data_list: List of bond information in same format as the cleaned csv file
    """
    def read_from_data_list(self, data_list):
        self.corporate_bonds = self.find_all_of_bond_type(data_list, 'corporate')
        self.government_bonds = self.find_all_of_bond_type(data_list, 'government')
        self.sort_bonds()

    """"
        Sort the corporate and government bonds by their term value.
        The sort operation was used in order to reduce the run time of the `calculate_yield_spread` function.
        By sorting we perform a O(nlogn) operation once per loading the dataset. This allows us to perform a binary
        search for the closest government bond term to a corporate bond's term. This search will now be O(logn) as 
        opposed to O(n) for each element in the corporate bonds list.
    """
    def sort_bonds(self):
        self.corporate_bonds.sort(key=lambda tup: tup[2])
        self.government_bonds.sort(key=lambda tup: tup[2])

    """
        Clean the data from the csv file and remove the excess information from the float values
    """
    @staticmethod
    def clean_numeric_values(data_list):
        new_data_list = []
        for data in data_list:
            row = data
            # CSV returns strings so need to convert to float.
            # To remove the " years" part of the string, cut off the last 6 characters
            row[2] = float(data[2][:-6])
            # Convert the string for yield to a float and remove the '%' character
            row[3] = float(data[3][:-1])
            new_data_list.append(row)
        return new_data_list

    """
        Seperate the data list depending on the type of bond.
    """
    @staticmethod
    def find_all_of_bond_type(data_list, bond_type):

        if bond_type != 'corporate' and bond_type != 'government':
            return None

        ret_list = []
        for data in data_list:
            if data[1] == bond_type:
                ret_list.append(data)
        return ret_list

    """
        Calculate the yield spread between a corporate bond and its government bond benchmark.
        Find the government bond that has a term as close as possible to the corporate bond, and 
        return the difference in yield.
        Goes through all the corporate bonds and finds the closest government bond.
        
        One alternative approach that was considered was to loop over all the government bonds and
        find the value that has the absolute minimum between the government bond term and 
        corporate bond term. This would mean and O(n) operation for each corporate bond. If the size of the corporate
        bonds is m this would result in an algorithm that is O(nm). For large n and m, this would be very slow. By 
        instead sorting the corporate bonds and government bonds, we can do this in O(mlogm) and O(nlogn) time. Next
        taking advantage of binary search, I have written the below algorithm to work in O(mlogn) time, hence the 
        run time of the algorithm is either O(mlogm), O(nlogm)(from sorting) or O(mlogn) depending on which takes the 
        longest. This leads to a faster algorithm than the O(nm) version.
    """
    def calculate_yield_spread(self):
        result = "bond,benchmark,spread_to_benchmark\n"
        for corp_data in self.corporate_bonds:

            best_gov_bond, _, _ = self.nearest_binary_search(self.government_bonds, corp_data[2])

            # Calculate the spread
            spread_to_benchmark = corp_data[3] - best_gov_bond[3]
            result += "{},{},{:.2f}%\n".format(corp_data[0], best_gov_bond[0], spread_to_benchmark)
        return result

    """
        Closest binary search where the function returns the element with the closest term value to val. 
        It also returns the left and right index, which is useful for finding the second challenge where we need to find
        the two government bonds that satisfy gov_bond1['term'] <= corp_bond['term'] <= gov_bond2['term']
    """

    @staticmethod
    def nearest_binary_search(bond_array, val):
        if val < bond_array[0][2]:
            return bond_array[0], 0, 1
        if val > bond_array[len(bond_array) - 1][2]:
            return bond_array[len(bond_array) - 1], len(bond_array) - 2, len(bond_array) - 1
        low = 0
        high = len(bond_array) - 1

        while low <= high:
            mid = (low + high)/2
            if val < bond_array[mid][2]:
                high = mid - 1
            elif val > bond_array[mid][2]:
                low = mid + 1
            else:
                return bond_array[mid], mid - 1, mid
        indices = sorted([high, low])
        low = indices[0]
        high = indices[1]
        if abs(bond_array[low][2] - val) < abs(val - bond_array[high][2]):
            return bond_array[low], low, low + 1
        else:
            return bond_array[high], high - 1, high

    """
        Find the spread to curve by first finding the two government bonds that satisfy: 
        gov_bond1['term'] <= corp_bond['term'] <= gov_bond2['term'] and then finding the equation of a line between the 
        two bonds. Using the term value from the corporate bond, the value for the interest along the line can be 
        interpolated. From this we can find the spread to the curve.
    """
    def calculate_spread_to_curve(self):
        result = "bond,spread_to_curve\n"
        for corp_data in self.corporate_bonds:

            best_gov_bond, left_index, right_index = self.nearest_binary_search(self.government_bonds, corp_data[2])

            points = [(self.government_bonds[left_index][2], self.government_bonds[left_index][3]),
                      (self.government_bonds[right_index][2], self.government_bonds[right_index][3])]

            m, b = self.find_equation_of_line_from_two_points(points)
            point_on_interpolated_line = m * corp_data[2] + b
            c_yield = corp_data[3]

            spread_to_curve = c_yield - point_on_interpolated_line
            result += "{},{:.2f}%\n".format(corp_data[0], spread_to_curve)
        return result

    """"
        Derive the equation of the line using two points. Points should be ordered where pt_1.x <= pt_2.x
    """
    @staticmethod
    def find_equation_of_line_from_two_points(points):
        m = float(points[1][1] - points[0][1]) / float(points[1][0] - points[0][0])
        b = points[1][1] - (m * points[1][0])

        return m, b


def main():
    spread_calculator = SpreadCalculator()
    spread_calculator.read_from_csv('sample_input.csv')
    print spread_calculator.calculate_yield_spread()
    print spread_calculator.calculate_spread_to_curve()

    spread_calculator = SpreadCalculator()
    spread_calculator.read_from_csv('challenge2.csv')
    print spread_calculator.calculate_spread_to_curve()

if __name__ == '__main__':
    main()