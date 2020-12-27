# README

### Description

This is a locally running Python Web application that calculates linear production plan based on given forecast and allowed pre build days.

```python
 .
├── app.py
├── format_table.py
├── linearProcess.py
├── readme.md
├── templates
│   └── index.html
├── test_cases
│   ├── input1.csv
│   ├── input1_expected.csv
│   ├── input2.csv
│   ├── input2_expected.csv
│   ├── input3.csv
│   ├── input3_expected.csv
│   ├── input4.csv
│   ├── input4_expected.csv
│   ├── input5.csv
│   ├── input5_expected.csv
│   ├── input6.csv
│   └── input6_expected.csv
├── tester.py
├── downloads
└── uploads
```

### Functionalities

- styled UI
- website input check
    - invalid file type
    - invalid pre build-days entry (0/blank/non-integer/float/character)
- preview of suggested production plan
- download access to the processed file

### How to Use

```python
''' To run the Web Application '''
# 1) use the terminal to go to the current directory, type 
			python3 app.py
# 2) open the browser and go to http://0.0.0.0:5000/

''' To run the tester'''
# use the terminal to go to the current directory, type 
			python3 tester.py
```

### Assumptions to the Problem

- The forecast is correct and meaningful
    - always cumulative, i.e., non-decreasing order
    - the last day always has a forecast demand (otherwise is not meaningful)
- For each product by site
    - day entries start from 0
    - day entries are consecutive, i.e., no missing days
- Input file contains 4 columns (site, product, day, demand)

### Approach

The task is divided into two parts: fill out the rest demand column and fill out the produce column. 

- For the demand column, we can simply do paddling/**front-filling** (fill downwards) to take care of the most empty part, since the demand is supposed to stay the same until new demand at key date is given. After paddling, the only empty rows that demand column may have are the initial days when demand has not arrived. Hence, we will fill out those rows by 0 to indicate this scenario.
- For the produce column, we need to create a key dates look-up table as well as additional temporary columns to store the intermediate/feature information below: previous key date, current planning winder, earliest start date, and initial demand.

    [Intermediate Variables](https://www.notion.so/52f2d96a85be4fe8b8ca9e52ac6dc96a)

    - The produce columns is then updated based on the following rules using the intermediate information:

        ```python
        				# BASE CASE A: initial stage
                if demand == 0:
                    if day >= start:    # if should've begun production
                        interval = plan_window-start+1
                        return init_demand/interval*(day-start+1)
                    else:               # if it's too early to start
                        return 0
                # BASE CASE B: key date
                if day == prevKDay+plan_window:
                    return demand
                # GENERAL CASE: 
                if plan_window > max_preBuildDays and day < start:   # if it's too early, halt production
                    return demand
                if plan_window < max_preBuildDays:
                    return np.nan  # should've begun production, return NaN for future linearization using pd.interpolate()
        ```

    An example of intermediate information for each row:

![README%20eb20e5c0ecd740f98dea81a5ca90df3c/Screen_Shot_2020-11-12_at_10.46.42_AM.png](README%20eb20e5c0ecd740f98dea81a5ca90df3c/Screen_Shot_2020-11-12_at_10.46.42_AM.png)

### Code Validation (Real World Business Scenarios)

```python
xiaodunDEREKs-Macbook-Pro:Apple_Interview_A1 DEREK$ python3 tester.py
......
----------------------------------------------------------------------
Ran 6 tests in 0.295s

OK
```

Six test cases are designed to cover real world scenarios as complete as possible. The description of each test case can be found in the [tester.py](http://tester.py) file.

```python
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
        ''' multiple sites + multiple products in same site '''
        res = linearize(PATH+'input6.csv',6) 
        expected = pd.read_csv(PATH+'input6_expected.csv')
        assert_frame_equal(res, expected)
```

![README%20eb20e5c0ecd740f98dea81a5ca90df3c/Screen_Shot_2020-11-11_at_10.46.32_PM.png](README%20eb20e5c0ecd740f98dea81a5ca90df3c/Screen_Shot_2020-11-11_at_10.46.32_PM.png)