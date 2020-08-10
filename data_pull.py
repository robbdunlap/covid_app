## This module retrieves the latest:
#       - COVID-19 infections from the JHU GitHub repository
#       - Community mobility information from Google
#       - CDC excess deaths probably caused by COVID-19 but classified as other causes
# These functions were separated to prevent data pulls being done more than necessary


import pandas as pd
import os

<<<<<<< HEAD
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
=======
###### import the data from JHU, Google, and CDC ######

# import the cumulative confirmed cases and cumulative confirmed deaths data from JHU GitHub repository
url_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
confirmed_cases = pd.read_csv(url_cases, error_bad_lines=False)
print('JHU confirmed cases downloaded')

url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
deaths = pd.read_csv(url_deaths, error_bad_lines=False)
print('JHU deaths downloaded')

# import the Google Mobility Report from https://www.google.com/covid19/mobility/index.html
url_gmr = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
gmr = pd.read_csv(url_gmr, error_bad_lines=False)
print('Google community mobility report downloaded')

# import the excess deaths data from CDC website
url_xs_deaths = ('https://data.cdc.gov/api/views/xkkf-xrst/rows.csv?accessType=DOWNLOAD&bom=true&format=true%20target=')
xs_deaths = pd.read_csv(url_xs_deaths, error_bad_lines=False)
print('CDC excess deaths data downloaded')


###### Save the Google and CDC data (JHU data has to be processed before saving) ######

# save the data as csv files for the other modules to use
gmr.to_csv('data/Global_Mobility_Report.csv', index=False)
xs_deaths.to_csv('data/xs_deaths.csv',index=False)

# delete dfs to save memory
del gmr
del xs_deaths


###### Generate the daily new cases and daily new deaths from the JHU cumulative case/deaths counts ######

# subtrack the previous days values from the current days values to get the daily new cases
# (do this all the way from the current day back to the first day of values to get the 
# daily new cases/deaths for each day)
>>>>>>> So many changes - totally new design

# while loop for daily new cases
first_data_col = 11  # this will always be the data fro 1/22/20 unless they change the file format
counter = len(confirmed_cases.columns) - 1  # this is the value to use with iloc to find the last column

<<<<<<< HEAD
# subtrack the previous days values from the current days values to get the daily new cases
# (do this all the way from the current day back to the first day of values to get the 
# daily new cases/deaths for each day)
print("Munging JHU Confirmed Cases")
=======
print('calculating new cases')
>>>>>>> So many changes - totally new design
while counter > first_data_col:
    prev_col_num = counter - 1
    confirmed_cases.iloc[:,counter] = confirmed_cases.iloc[:,counter] - confirmed_cases.iloc[:,prev_col_num] 
    counter -= 1
<<<<<<< HEAD
confirmed_cases.to_csv('data/jhu_confirmed_daily.csv',index=False)
del confirmed_cases

print("Downloading JHU Deaths")
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
deaths = pd.read_csv(url_deaths, error_bad_lines=False)
=======
>>>>>>> So many changes - totally new design

# while loop for daily new deaths
first_data_col = 12  # this will always be the data fro 1/22/20 unless they change the file format
counter = len(deaths.columns) - 1  # this is the value to use with iloc to find the last column

<<<<<<< HEAD
print("Munging JHU Deaths")
=======
print('caclulating new deaths')
>>>>>>> So many changes - totally new design
while counter > first_data_col:
    prev_col_num = counter - 1
    deaths.iloc[:,counter] = deaths.iloc[:,counter] - deaths.iloc[:,prev_col_num] 
    counter -= 1
deaths.to_csv('data/jhu_deaths_daily.csv',index=False)
print("Done")









<<<<<<< HEAD

=======
# save the data as csv files for the other modules to use
confirmed_cases.to_csv('data/jhu_confirmed_daily.csv',index=False)
deaths.to_csv('data/jhu_deaths_daily.csv',index=False)
>>>>>>> So many changes - totally new design



# # This section is for preprossing the population data from the US Census Bureau. The data 
# # won't chage during the timeframe of this study so it only needed to be downloaded and 
# # preprocessed once, hence the code is commented out.

# #-----------------------------------------------------------------------------------
# # data is from US Census Bureau - 2019 population estimates
# # https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/
# state_pop = pd.read_csv("SCPRC-EST2019-18+POP-RES.csv")

# indexNames = state_pop[ (state_pop['NAME'] == 'United States') | (state_pop['NAME'] == 'Puerto Rico Commonwealth') ].index
# state_pop.drop(indexNames , inplace=True)  

# columns_to_drop = ['SUMLEV','REGION','DIVISION','STATE','POPEST18PLUS2019','PCNT_POPEST18PLUS']
# state_pop.drop(columns_to_drop, axis=1, inplace=True)

# # save dataframe as csv
# state_pop.to_csv('data/state_pop.csv', index=False)
# #-----------------------------------------------------------------------------------