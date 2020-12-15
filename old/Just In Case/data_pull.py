## This module retrieves the latest:
#       - COVID-19 infections from the JHU GitHub repository
#       - Community mobility information from Google
#       - CDC excess deaths probably caused by COVID-19 but classified as other causes
# These functions were separated to prevent data pulls being done more than necessary


import pandas as pd
import os

os.makedirs("data", exist_ok=True)

######## import the Google Mobility Report from https://www.google.com/covid19/mobility/index.html ##########
print("Downloading Google Community Mobility Report")
url_gmr = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
gmr = pd.read_csv(url_gmr, error_bad_lines=False)
gmr.to_csv('data/Global_Mobility_Report.csv', index=False)
del gmr

############## grab excess deaths data from CDC website #######################
print("Downloading CDC Excess Deaths")
url_xs_deaths = ('https://data.cdc.gov/api/views/xkkf-xrst/rows.csv?accessType=DOWNLOAD&bom=true&format=true%20target=')
xs_deaths = pd.read_csv(url_xs_deaths, error_bad_lines=False)
xs_deaths.to_csv('data/xs_deaths.csv',index=False)
del xs_deaths

###### import the cumulative confirmed cases and cumulative confirmed deaths data from JHU GitHub repository ##########
print("Downloading JHU Confirmed Cases")
url_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
confirmed_cases = pd.read_csv(url_cases, error_bad_lines=False)

# while loop for daily new cases
first_data_col = 11  # this will always be the data fro 1/22/20 unless they change the file format
counter = len(confirmed_cases.columns) - 1  # this is the value to use with iloc to find the last column

# subtrack the previous days values from the current days values to get the daily new cases
# (do this all the way from the current day back to the first day of values to get the 
# daily new cases/deaths for each day)
print("Munging JHU Confirmed Cases")
while counter > first_data_col:
    prev_col_num = counter - 1
    confirmed_cases.iloc[:,counter] = confirmed_cases.iloc[:,counter] - confirmed_cases.iloc[:,prev_col_num] 
    counter -= 1
confirmed_cases.to_csv('data/jhu_confirmed_daily.csv',index=False)
del confirmed_cases

print("Downloading JHU Deaths")
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
deaths = pd.read_csv(url_deaths, error_bad_lines=False)

# while loop for daily new deaths
first_data_col = 12  # this will always be the data fro 1/22/20 unless they change the file format
counter = len(deaths.columns) - 1  # this is the value to use with iloc to find the last column

print("Munging JHU Deaths")
while counter > first_data_col:
    prev_col_num = counter - 1
    deaths.iloc[:,counter] = deaths.iloc[:,counter] - deaths.iloc[:,prev_col_num] 
    counter -= 1
deaths.to_csv('data/jhu_deaths_daily.csv',index=False)
print("Done")











