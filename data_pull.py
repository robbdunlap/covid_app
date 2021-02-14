## This module retrieves the latest:
#       - COVID-19 infections from the JHU GitHub repository
#       - Community mobility information from Google
#       - CDC excess deaths probably caused by COVID-19 but classified as other causes
# These functions were separated to prevent data pulls being done more than necessary


import pandas as pd
import os
import requests
#from bs4 import BeautifulSoup

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


###### import the CDC COVID-19 daily count of diagnostic testing in each state ##########
print("Downloading CDC COVID-19 daily count of diagnostic testing in each state")
healtdata_api = requests.get("https://healthdata.gov/data.json")
healthdata_json = healtdata_api.json()

for each_element in healthdata_json['dataset']:
        #if each_element['identifier'] == 'fe3c12ae-bdba-49eb-a9fa-5ab44a95b0ae':  # this identifier has changed but the API doesn't reflect this
        if each_element['identifier'] == 'c13c00e3-f3d0-4d49-8c43-bf600a6c0a0d':
            for sub_element in each_element['distribution']:
                if sub_element['format'] == 'csv':
                    covid_testing_data_url =  sub_element['downloadURL']

covid_testing_data = pd.read_csv(covid_testing_data_url, error_bad_lines=False)
covid_testing_data.to_csv('data/covid_testing_data_filecovid-19_diagnostic_lab_testing.csv',index=False)

print("That's it, all done!")  

# This is what I was using before learning how to use the healthdata.gov/data.json API
# # I couldn't figure out how to use the DKAN API that healthdata.gov uses (it only returned 10 records)
# # The CSV download link on the page uses the report date as part of the URL so it changes each day.
# # So, I used BeautifulSoup to extract the CSV download link to then read it into a dataframe.

# print("Downloading CDC Daily Testing Data")
# covid_testing_page_url = 'https://healthdata.gov/dataset/covid-19-diagnostic-laboratory-testing-pcr-testing-time-series'
# covid_testing_page_data = requests.get(covid_testing_page_url).text
# soup = BeautifulSoup(covid_testing_page_data, 'html.parser')

# soup_link_list = []
# for link in soup.find_all('a'):
#     soup_link_list.append(link.get('href'))

# for link in soup_link_list:
#     if link == None:
#         pass
#     else:
#         if link[:74] == 'https://healthdata.gov/sites/default/files/covid-19_diagnostic_lab_testing':
#             covid_test_data_url = link
#             break

# covid_testing_data_filename = covid_test_data_url[43:]
# covid_testing_data = pd.read_csv(covid_test_data_url, error_bad_lines=False)
# covid_testing_data.to_csv(f'data/covid_testing_data_backup/{covid_testing_data_filename}',index=False)
# covid_testing_data.to_csv('data/covid_testing_data_filecovid-19_diagnostic_lab_testing.csv',index=False)
    
  
# # This section is for preprossing the population data from the US Census Bureau. The data 
# # won't chage during the timeframe of this study so it only needed to be downloaded and 
# # preprocessed once, hence the code is commented out. If

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