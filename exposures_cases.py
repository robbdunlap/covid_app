import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

weekly_est_cases_deaths = pd.read_csv("data/weekly_est_cases_deaths.csv")

# List of state to use in the loop to process the data for each state
list_of_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', \
                  'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', \
                  'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', \
                  'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', \
                  'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', \
                  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

lin_regres_model = pd.DataFrame()

for state_selected in list_of_states:
    current_week_for_state = weekly_est_cases_deaths[(weekly_est_cases_deaths['state'] == state_selected)].copy()
    current_week_for_state = current_week_for_state[['date','est_inf','enc_w_inf','est_inf_per_100k']]

    next_week_for_state = current_week_for_state[['date','est_inf','est_inf_per_100k']].shift().copy()
    next_week_for_state.rename(columns={'date':'date_inf_occ_on','est_inf':'infect_1_week_later',
                                    'est_inf_per_100k':'est_inf_per_100k_week_ltr'}, inplace=True)

    curr_and_next_for_state = current_week_for_state.join(next_week_for_state)
    curr_and_next_for_state.dropna(inplace=True)

    X = pd.DataFrame(curr_and_next_for_state['enc_w_inf'])
    y = curr_and_next_for_state['est_inf_per_100k_week_ltr']

    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(X, y)

    # Make predictions using the testing set
    hyp = regr.predict(X)

    mse = mean_squared_error(y, hyp)
    coeff_determ = r2_score(y, hyp)

    append_dict = {'State':state_selected, 'intercept':regr.intercept_, 'coeff':regr.coef_[0], 'mse':mse, 'coeff_determ':coeff_determ}

    lin_regres_model = lin_regres_model.append(append_dict, ignore_index = True)

    del append_dict

# save the data to a csv for the display module
lin_regres_model.to_csv('data/exposure_model.csv', index=False)


