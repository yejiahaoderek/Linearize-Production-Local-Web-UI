'''
tester.py
- run tester on test cases to evaluate the performance of the algorithm
@ Jiahao (Derek) Ye
'''

import pandas as pd
from linearProcess import linearize
import unittest 
import os
from pandas.testing import assert_frame_equal

PATH = os.path.dirname(os.path.realpath(__file__))+ '/test_cases/'
  
class TestLinearPlanner(unittest.TestCase): 
  
    def test_case1(self): 
        ''' interview example '''
        res = linearize(PATH+'input1.csv',6) 
        expected = pd.read_csv(PATH+'input1_expected.csv')
        assert_frame_equal(res, expected)
  
    def test_case2(self): 
        ''' interview example w/noises '''
        res = linearize(PATH+'input2.csv',6) 
        expected = pd.read_csv(PATH+'input2_expected.csv')
        assert_frame_equal(res, expected)
  
    def test_case3(self): 
        ''' available days to produce < pre build-day '''
        res = linearize(PATH+'input3.csv',6) 
        expected = pd.read_csv(PATH+'input3_expected.csv')
        assert_frame_equal(res, expected)
  
    def test_case4(self): 
        ''' available days to produce == pre build-day '''
        res = linearize(PATH+'input4.csv',6) 
        expected = pd.read_csv(PATH+'input4_expected.csv')
        assert_frame_equal(res, expected)

    def test_case5(self): 
        ''' available days to produce > pre build-day '''
        res = linearize(PATH+'input5.csv',6) 
        expected = pd.read_csv(PATH+'input5_expected.csv')
        assert_frame_equal(res, expected)

    def test_case6(self): 
        ''' multiple sites
         + multiple products in same site 
         + some products demand came in a later day
         '''
        res = linearize(PATH+'input6.csv',6) 
        expected = pd.read_csv(PATH+'input6_expected.csv')
        assert_frame_equal(res, expected)
  
if __name__ == '__main__': 
    unittest.main() 