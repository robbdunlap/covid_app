# this module converts the Google mobility data into exposure indexes.
# this index is a thought experiment and there are HUGE assumptions in it.


import pandas as pd

mobility_data = pd.read_csv("data/Global_Mobility_Report.csv")

# drop non-US data
mobility_data.drop(mobility_data.loc[mobility_data['country_region_code'] != "US"].index, inplace=True)

# convert date column to datetime formate and rename to Date
mobility_data['date'] = pd.to_datetime(mobility_data['date'])
mobility_data.rename({'date':'Date'}, axis='columns', inplace=True)

# List of state to use in the loop to process the data for each state
list_of_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', \
                  'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', \
                  'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', \
                  'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', \
                  'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', \
                  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

# create an empty df to receive the processed data
df_columns = ['country_region_code',
 'country_region',
 'sub_region_1',
 'sub_region_2',
 'iso_3166_2_code',
 'census_fips_code',
 'Date',
 'retail_and_recreation_percent_change_from_baseline',
 'grocery_and_pharmacy_percent_change_from_baseline',
 'parks_percent_change_from_baseline',
 'transit_stations_percent_change_from_baseline',
 'workplaces_percent_change_from_baseline',
 'residential_percent_change_from_baseline',
 'retail_and_recreation_percent_change_from_baseline_rolling_avg',
 'grocery_and_pharmacy_percent_change_from_baseline_rolling_avg',
 'parks_percent_change_from_baseline_rolling_avg',
 'transit_stations_percent_change_from_baseline_rolling_avg',
 'workplaces_percent_change_from_baseline_rolling_avg',
 'residential_percent_change_from_baseline_rolling_avg',
 'retail_n_rec_normal_exp_per_day',
 'groc_n_pharm_normal_exp_per_day',
 'parks_normal_exp_per_day',
 'trans_stat_normal_exp_per_day',
 'work_normal_exp_per_day',
 'res_normal_exp_per_day',
 'retail_n_rec_strict_exp_per_day',
 'groc_n_pharm_strict_exp_per_day',
 'parks_strict_exp_per_day',
 'trans_stat_strict_exp_per_day',
 'work_strict_exp_per_day',
 'res_strict_exp_per_day',
 'retail_n_rec_relaxed_exp_per_day',
 'groc_n_pharm_relaxed_exp_per_day',
 'parks_relaxed_exp_per_day',
 'trans_stat_relaxed_exp_per_day',
 'work_relaxed_exp_per_day',
 'res_relaxed_exp_per_day',
 'normal_exposure_per_day',
 'strict_exposure_per_day',
 'relaxed_exposure_per_day']
all_state_mob_data = pd.DataFrame(columns = df_columns)
all_state_mob_data['Date'] = pd.to_datetime(all_state_mob_data['Date'])

# loop through the data to process the data for each state
for state_selected in list_of_states:
    print(state_selected)
    # subselect state data
    state_mob_data = mobility_data.drop(mobility_data.loc[mobility_data['sub_region_1'] \
                                         != state_selected].index)
    
    #state_mobility_data = state_mob_data.drop(mobility_data.loc[mobility_data['sub_region_1'].isna()].index)
    
    
    # subselect just the data from the state that doesn't have a county listed 
    state_mobility_data = state_mob_data[state_mob_data['sub_region_2'].isna()]
    
    # create an explicit copy of the dataframe to avoid the "A value is trying to be set on a copy of a slice from 
    # a DataFrame." Pandas warning
    state_mobility_data = state_mobility_data.copy()
    
    # calculate a rolling 7-day average for the 'precent change columns'
    column_titles = ['retail_and_recreation_percent_change_from_baseline', \
                    'grocery_and_pharmacy_percent_change_from_baseline', \
                    'parks_percent_change_from_baseline', \
                    'transit_stations_percent_change_from_baseline', \
                    'workplaces_percent_change_from_baseline', \
                    'residential_percent_change_from_baseline']
    for cat_item in column_titles:
        column_title = cat_item + '_rolling_avg'
        state_mobility_data[column_title] = \
        state_mobility_data[cat_item].rolling(window=7, center=False).mean()
        
    # the values in the embedded lists in the dictionary are "column titles" of the locations istn state_mobility_data, 
    # baseline hours spent in those locations, exposure rates in those locations under "normal" conditions,
    # exposure rates in those locations under "strict" social distancing conditions, and exposure rates in those 
    # locations under "relaxed" social distancing conditions
    column_name_dict = {
                "retail_n_rec": ['retail_and_recreation_percent_change_from_baseline_rolling_avg', 1, 50, 5, 15], 
                "groc_n_pharm": ['grocery_and_pharmacy_percent_change_from_baseline_rolling_avg', 1, 100, 10, 30],
                "parks": ['parks_percent_change_from_baseline_rolling_avg', 0.25, 10, 1, 3],
                "trans_stat": ['transit_stations_percent_change_from_baseline_rolling_avg', 0.25, 20, 2, 6],
                "work": ['workplaces_percent_change_from_baseline_rolling_avg', 8.75, 20, 2, 6],
                "res": ['residential_percent_change_from_baseline_rolling_avg', 12.75, 1, 0.1, 0.3]
                }

    # calculate the daily exposure for the average person in each 'location' bucket under "normal" conditions
    for item in column_name_dict:
        new_column_title = item + '_normal_exp_per_day'
        mobility_column = column_name_dict[item][0]
        baseline_hours = column_name_dict[item][1]
        exposure_rate = column_name_dict[item][2]
        
        state_mobility_data[new_column_title] = \
        ((state_mobility_data[mobility_column]/100 * baseline_hours) + baseline_hours)* exposure_rate
        
    # calcuate the daily exposure for the average person in each 'location' bucket under "strict" social distancing conditions
    for item in column_name_dict:
        new_column_title = item + '_strict_exp_per_day'
        mobility_column = column_name_dict[item][0]
        baseline_hours = column_name_dict[item][1]
        exposure_rate = column_name_dict[item][3]
        
        state_mobility_data[new_column_title] = \
        ((state_mobility_data[mobility_column]/100 * baseline_hours) + baseline_hours)* (exposure_rate)

    # calcuate the daily exposure for the average person in each 'location' bucket under "relaxed" social distancing conditions
    for item in column_name_dict:
        new_column_title = item + '_relaxed_exp_per_day'
        mobility_column = column_name_dict[item][0]
        baseline_hours = column_name_dict[item][1]
        exposure_rate = column_name_dict[item][4]
        
        state_mobility_data[new_column_title] = \
        ((state_mobility_data[mobility_column]/100 * baseline_hours) + baseline_hours)* exposure_rate
    
    # sum the exposure buckets for "normal" conditions
    sum_column = state_mobility_data['retail_n_rec_normal_exp_per_day'] + state_mobility_data['groc_n_pharm_normal_exp_per_day'] + \
    state_mobility_data['parks_normal_exp_per_day'] + state_mobility_data['trans_stat_normal_exp_per_day'] + \
    state_mobility_data['work_normal_exp_per_day'] + state_mobility_data['res_normal_exp_per_day']

    state_mobility_data['normal_exposure_per_day'] = sum_column

    # sum the exposure buckets for "strict" conditions
    sum_column = state_mobility_data['retail_n_rec_strict_exp_per_day'] + state_mobility_data['groc_n_pharm_strict_exp_per_day'] + \
    state_mobility_data['parks_strict_exp_per_day'] + state_mobility_data['trans_stat_strict_exp_per_day'] + \
    state_mobility_data['work_strict_exp_per_day'] + state_mobility_data['res_strict_exp_per_day']

    state_mobility_data['strict_exposure_per_day'] = sum_column

    # sum the exposure buckets for "relaxed" conditions
    sum_column = state_mobility_data['retail_n_rec_relaxed_exp_per_day'] + state_mobility_data['groc_n_pharm_relaxed_exp_per_day'] + \
    state_mobility_data['parks_relaxed_exp_per_day'] + state_mobility_data['trans_stat_relaxed_exp_per_day'] + \
    state_mobility_data['work_relaxed_exp_per_day'] + state_mobility_data['res_relaxed_exp_per_day']

    state_mobility_data['relaxed_exposure_per_day'] = sum_column


    ################################################################    
    
    
    ################################################################
    # the append doesn't work without reassigning it back to the df
    # https://stackoverflow.com/questions/51997818/pandas-append-not-working/51997965
    all_state_mob_data = all_state_mob_data.append(state_mobility_data, ignore_index = True)
     
    
    # drop intermediate dfs each loop
    del state_mob_data
    del state_mobility_data

all_state_mob_data.to_csv("data/all_state_mob_data.csv", index=False)
