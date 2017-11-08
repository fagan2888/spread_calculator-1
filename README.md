# Spread Calculator Challenge

This library provides functions to calculate the spread benchmark and spread to the government bond curve. 
This library provides an efficient calculation of both algorithms giving a O(nlogm) runtime, where n is the number of 
corportate bonds in the csv and m is the number of government bonds in the csv file. 
This is accomplished by sorting the bonds by their term duration, which is done in O(nlogn) and then using a nearest 
binary search algorithm to find the closest government bond to each corporate bond. Hence for each n corporate bonds,
the binary search is run in O(logm), hence the runtime is O(nlogm). This is faster than the O(n*m) solution, where you 
compare each corporate bond with each government bond and find the closest match.

To run the code first make sure to have python installed and you are using python 2.7. 
To run the main file to demonstrate the results on the sample_input.csv and challenge2.csv simply run:

```
    python spread_calculator.py
```

In order to check if the unit tests are correct run:

```
    python -m unittest discover
```

You should then see:

```
........
----------------------------------------------------------------------
Ran 8 tests in 0.001s

OK

```