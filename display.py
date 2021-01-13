# type "streamlit run streamlit_covid_data_app.py" at the command prompt to run

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import plotly.express as px
#import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import SU
import numpy as np

# import data files
weekly_est_cases_deaths = pd.read_csv("data/weekly_est_cases_deaths.csv")
weekly_est_cases_deaths['date'] =  pd.to_datetime(weekly_est_cases_deaths['date'])

# import proportion of population infected to date
proportion_pop_infected = pd.read_csv("data/proportion_pop_infected.csv", usecols=['state','est_proportion_infected','rep_proportion_infected'])
proportion_pop_infected.rename(columns={'state':'State','est_proportion_infected':'Estimated Percent Infected','rep_proportion_infected':'Reported Percent Infected'}, inplace=True)

# import total reported and estimated percent of US population infected to date
file_path = 'data/estimated_percent_US_infected.txt'
with open(file_path, 'r') as filetoread:
    percent_total_us_pop_est_infected = filetoread.read()

file_path = 'data/reported_percent_US_infected.txt'
with open(file_path, 'r') as filetoread:
    percent_total_us_pop_reported_infected = filetoread.read()

# grab a list of the states'/territories' names fromt the df so that streamlit can display a drop-down selector 
states = weekly_est_cases_deaths.state.unique()

# grab the latest date of the JHU and GCMD to let the user know how fresh the data is
file_path_JHU = 'data/latest_date_of_JHU_data.txt'
file_path_GMD = 'data/latest_date_of_GMD.txt'
file_path_HealthData = 'data/latest_date_of_test_positivity_data.txt'
file_path_CDC = 'data/latest_date_of_excess_deaths_data.txt'
file_path_explainer_text = 'data/est_deaths_calc_explanation.txt'
file_path_exposure_explainer_text = 'data/explanation_of_exposure_calc.txt'

with open(file_path_JHU, 'r') as filetoread:
    latest_date_of_JHU_data = filetoread.read()
with open(file_path_GMD, 'r') as filetoread:
    latest_date_of_GMD = filetoread.read()
with open(file_path_HealthData, 'r') as filetoread:
    latest_date_of_test_positivity_data = filetoread.read()
with open(file_path_CDC, 'r') as filetoread:
    latest_date_of_excess_deaths_data = filetoread.read()
with open(file_path_explainer_text, 'r') as filetoread:
    est_deaths_calc_explanation = filetoread.read()
with open(file_path_exposure_explainer_text, 'r') as filetoread:
    est_exposures_calc_explanation = filetoread.read()


# title the page
st.title('Estimating COVID-19 Prevalence in the US')
st.title('')   # padding to separate page title from graphs

# streamlit selectbox for selecting which state to plot
st.sidebar.title('Choose 2 States to Compare')
state_1_selected = st.sidebar.selectbox('Select state of interest #1', states, index=(46))
state_2_selected = st.sidebar.selectbox('Select state of interest #2', states, index=(20))

# subselect the data for the selected state from the dataframe
df_for_display1 = weekly_est_cases_deaths[weekly_est_cases_deaths.state.isin([state_1_selected])]
df_for_display2 = weekly_est_cases_deaths[weekly_est_cases_deaths.state.isin([state_2_selected])]

# show latest date of data on the dashboard
for i in range(1,4):     # padding
    st.sidebar.title('')   

st.sidebar.title('Data Sources and Currency')
st.sidebar.markdown('[Reported COVID infections and deaths] \
                    (https://github.com/CSSEGISandData/COVID-19) \
                     is from JHU dataset as of:')
st.sidebar.markdown(f'**{latest_date_of_JHU_data}**')

st.sidebar.markdown('[Test positivity data] \
                    (https://healthdata.gov/dataset/covid-19-diagnostic-laboratory-testing-pcr-testing-time-series) \
                     is from HealthData.gov as of:')
st.sidebar.markdown(f'**{latest_date_of_test_positivity_data}**')

st.sidebar.markdown('[Excess deaths in US data] \
                    (https://www.cdc.gov/nchs/nvss/vsrr/covid19/excess_deaths.htm) \
                     from the CDC as of:')
st.sidebar.markdown(f'**{latest_date_of_excess_deaths_data}**')

st.sidebar.markdown('Mobility index is derived from [Google Mobility Data] \
                    (https://www.google.com/covid19/mobility/index.html) \
                     as of:')
st.sidebar.markdown(f'**{latest_date_of_GMD}**')


# Total estimated US cases vs. reported in JHU data
total_weekly_us_cases = weekly_est_cases_deaths[['est_inf','new_cases_jhu']].groupby(weekly_est_cases_deaths['date']).sum()
total_weekly_us_cases.reset_index(level=0, inplace=True)
total_weekly_us_cases[['est_inf','new_cases_jhu']] = total_weekly_us_cases[['est_inf','new_cases_jhu']].fillna(0)
total_weekly_us_cases['est_inf'] = total_weekly_us_cases['est_inf'].astype(int)
total_weekly_us_cases.replace(0, np.nan, inplace=True) 
total_weekly_us_cases.rename(columns={'date': 'Date', 'new_cases_jhu': 'JHU Reported Infections', 'est_inf': 'Estimated Actual Infections'}, inplace=True)

# data for state 1 charting
df_for_display_state1_changed_names = df_for_display1[['date', 'new_cases_per_100k', 'est_inf_per_100k', 'test_positivity_rate', 'weekly_exposures']].copy()
df_for_display_state1_changed_names.rename(columns={'date':'Date','new_cases_per_100k':'JHU Reported','est_inf_per_100k':'Est Actual Inf',
                                                    'test_positivity_rate':'Test Positivity Rate', 'weekly_exposures':'Weekly Exposure Rate', 
                                                    'density_cor_exposure':'Density Corrected Exposures'}, inplace=True)

# data for state 2 charting
df_for_display_state2_changed_names = df_for_display2[['date', 'new_cases_per_100k', 'est_inf_per_100k', 'test_positivity_rate', 'weekly_exposures']].copy()
df_for_display_state2_changed_names.rename(columns={'date':'Date','new_cases_per_100k':'JHU Reported','est_inf_per_100k':'Est Actual Inf',
                                                    'test_positivity_rate':'Test Positivity Rate', 'weekly_exposures':'Weekly Exposure Rate', 
                                                    'density_cor_exposure':'Density Corrected Exposures'}, inplace=True)

### melt data for exposures per week plotting
df_exposure_data = weekly_est_cases_deaths[['date', 'state', 'weekly_exposures', 'density_cor_exposure', 'enc_w_inf']].copy()

# for weekly exposures
df_exposure_data_sel_states = df_exposure_data[(df_exposure_data['state'] == state_1_selected) | (df_exposure_data['state'] == state_2_selected)].copy()
df_exposure_data_sel_states.dropna(inplace=True)
df_exposure_data_sel_states_melt = pd.melt(df_exposure_data_sel_states, id_vars=['date','state'], value_vars = ['weekly_exposures']).sort_values(by=['date'])
df_exposure_data_sel_states_melt.drop('variable', axis=1, inplace=True)
df_exposure_data_sel_states_melt = df_exposure_data_sel_states_melt.rename(columns={'value':'Exposures per week'})

# for density corrected weekly exposures
df_corr_exposure_data_sel_states = df_exposure_data[(df_exposure_data['state'] == state_1_selected) | (df_exposure_data['state'] == state_2_selected)].copy()
df_corr_exposure_data_sel_states.dropna(inplace=True)
df_corr_exposure_data_sel_states_melt = pd.melt(df_corr_exposure_data_sel_states, id_vars=['date','state'], value_vars = ['density_cor_exposure']).sort_values(by=['date'])
df_corr_exposure_data_sel_states_melt.drop('variable', axis=1, inplace=True)
df_corr_exposure_data_sel_states_melt = df_corr_exposure_data_sel_states_melt.rename(columns={'value':'Density corrected exposures per week'})

# for density corrected weekly encounters with infectious
df_corr_encounters_w_infectious_data_sel_states = df_exposure_data[(df_exposure_data['state'] == state_1_selected) | (df_exposure_data['state'] == state_2_selected)].copy()
df_corr_encounters_w_infectious_data_sel_states.dropna(inplace=True)
df_corr_encounters_w_infectious_data_sel_states_melt = pd.melt(df_corr_encounters_w_infectious_data_sel_states, id_vars=['date','state'], value_vars = ['enc_w_inf']).sort_values(by=['date'])
df_corr_encounters_w_infectious_data_sel_states_melt.drop('variable', axis=1, inplace=True)
df_corr_encounters_w_infectious_data_sel_states_melt = df_corr_encounters_w_infectious_data_sel_states_melt.rename(columns={'value':'Infectious encounters per week'})

#=======================================================
# chart plotting 
#=======================================================

### Total Reported US Cases vs. Estimated Cases

# Display of latest totals
st.markdown('___')
st.header(f'Total Percent of the US Population Reported Infected to Date: **{percent_total_us_pop_reported_infected}**')
st.header(f'Total Percent of the US Population Estimated Infected to Date: **{percent_total_us_pop_est_infected}**')
st.markdown('___')
#st.header('')

# Chart title and legends
x_axis_title_new_est_inf_100k =  'Date'
y_axis_title_new_est_inf_100k =  'New Cases per Week'

# State 1 Chart
fig1 = px.line(total_weekly_us_cases, 
             x="Date", 
             y=["JHU Reported Infections", "Estimated Actual Infections"], 
             labels={"variable":"Data Source"},
             title = f"<b>Reported and Estimated New Cases per 100K in the US</b>")
fig1.update_yaxes(title_text=y_axis_title_new_est_inf_100k)
fig1.update_xaxes(showgrid=True, title_text=x_axis_title_new_est_inf_100k)
fig1.update_layout(
    xaxis_tickformat = '%b<br>%Y')
fig1.update_traces(hovertemplate=None, hoverinfo='skip')

st.plotly_chart(fig1, use_container_width=True)

st.markdown(est_deaths_calc_explanation)

# Proportion of the population infected to date
st.header("**Latest Estimated vs Reported Percent of Each State's Population Infected to Date**")
dfStyler = proportion_pop_infected.style.set_properties(**{'font-size': '10pt',})\
                                        .format({'Estimated Percent Infected':'{:.1%}','Reported Percent Infected':'{:.1%}'})
st.dataframe(dfStyler)


# Padding
st.header('')
st.markdown('___')

# title separating the total US data from the two state comparison graphs
st.title('COVID-19 Data by US State')
st.title('')   # padding to separate page title from graphs

### Reported vs. Estimated Cases

# Chart title and legends
x_axis_title_new_est_inf_100k =  'Date'
y_axis_title_new_est_inf_100k =  'New Cases per 100K per Week'

# State 1 Chart
fig2 = px.line(df_for_display_state1_changed_names, 
             x="Date", 
             y=["JHU Reported", "Est Actual Inf"], 
             title = f"Reported and Estimated New Cases per 100K in {state_1_selected}",
             labels={"variable":"Data Source"},
             hover_name='Date')
fig2.update_yaxes(title_text=y_axis_title_new_est_inf_100k)
fig2.update_xaxes(showgrid=True, title_text=x_axis_title_new_est_inf_100k)
fig2.update_layout(
    xaxis_tickformat = '%b<br>%Y')

st.plotly_chart(fig2, use_container_width=True)

# State 2 Chart
fig3 = px.line(df_for_display_state2_changed_names, 
             x="Date", 
             y=["JHU Reported", "Est Actual Inf"], 
             title = f"Reported and Estimated New Cases per 100K in {state_2_selected}",
             labels={"variable":"Data Source"},
             hover_name='Date')
fig3.update_yaxes(title_text=y_axis_title_new_est_inf_100k)
fig3.update_xaxes(showgrid=True, title_text=x_axis_title_new_est_inf_100k)
fig3.update_layout(
    xaxis_tickformat = '%b<br>%Y')

st.plotly_chart(fig3, use_container_width=True)




### estimated infections vs. test positivity rate

# graph title and labels for State 1
inf_vs_positivity_title = f'Estimated Infections vs. Test Positivity Rate for {state_1_selected}'
y_axis_2_title_inf_vs_positivity = 'Test Positivity Rate'

# State 1 Chart
base = alt.Chart(df_for_display_state1_changed_names).encode(
    alt.X('Date:T', axis=alt.Axis(title=x_axis_title_new_est_inf_100k))).properties(
        title=inf_vs_positivity_title
    )

cases = base.mark_area(color='#858ce6').encode(
    alt.Y('Est Actual Inf:Q', 
    axis=alt.Axis(title=y_axis_title_new_est_inf_100k, titleColor='#858ce6'))
)

positivity = base.mark_line(color='#9c2927').encode(
    alt.Y('Test Positivity Rate:Q', 
    axis=alt.Axis(title=y_axis_2_title_inf_vs_positivity, titleColor='#9c2927'),
    scale=alt.Scale())
)

new = alt.layer(cases, positivity).resolve_scale(y='independent').configure_axisLeft(labelColor='#858ce6').configure_axisRight(labelColor='#9c2927')

st.altair_chart(new, use_container_width=True)

# graph title and labels for State 2
inf_vs_positivity_title = f'Estimated Infections vs. Test Positivity Rate for {state_2_selected}'
y_axis_2_title_inf_vs_positivity = 'Test Positivity Rate'

# State 2 Chart
base = alt.Chart(df_for_display_state2_changed_names).encode(
    alt.X('Date:T', axis=alt.Axis(title=x_axis_title_new_est_inf_100k))).properties(
        title=inf_vs_positivity_title
    )

cases = base.mark_area(color='#858ce6').encode(
    alt.Y('Est Actual Inf:Q', 
    axis=alt.Axis(title=y_axis_title_new_est_inf_100k, titleColor='#858ce6'))
)

positivity = base.mark_line(color='#9c2927').encode(
    alt.Y('Test Positivity Rate:Q', 
    axis=alt.Axis(title=y_axis_2_title_inf_vs_positivity, titleColor='#9c2927'),
    scale=alt.Scale())
)

new = alt.layer(cases, positivity).resolve_scale(y='independent').configure_axisLeft(labelColor='#858ce6').configure_axisRight(labelColor='#9c2927')

st.altair_chart(new, use_container_width=True)


### Weekly Exposures State1 vs. State2

st.markdown('___')
st.markdown(est_exposures_calc_explanation)
st.header('')

# graph title and labels for State 1
# Mobility = f'Estimated Infections vs. Test Positivity Rate for {state_1_selected}'
# y_axis_2_title_inf_vs_positivity = 'Test Positivity Rate'

# Exposures per Week Chart
chart = alt.Chart(df_exposure_data_sel_states_melt).mark_line().encode(
    x=alt.X('date', axis=alt.Axis(title='Date')),
    y='Exposures per week',
    color='state',
).properties(title=f'Potential Exposures per Week in {state_1_selected} vs. {state_2_selected}')
st.altair_chart(chart, use_container_width=True)

# Density Corrected Exposures per Week Chart
chart = alt.Chart(df_corr_exposure_data_sel_states_melt).mark_line().encode(
    x=alt.X('date', axis=alt.Axis(title='Date')),
    y='Density corrected exposures per week',
    color='state',
).properties(title=f'Population Density Corrected Potential Exposures per Week in {state_1_selected} vs. {state_2_selected}')
st.altair_chart(chart, use_container_width=True)



# Density Corrected Ecounters with Infectious per Week Chart
# title is too long for graph so putting it in as markdown instead
st.markdown("### **Estimated Number of Encounters per Week with Someone who's Infectious in:**")
title_for_graph = f'### **{state_1_selected} vs. {state_2_selected}**'
st.markdown(title_for_graph)

chart = alt.Chart(df_corr_encounters_w_infectious_data_sel_states_melt).mark_line().encode(
    x=alt.X('date', axis=alt.Axis(title='Date')),
    y='Infectious encounters per week',
    color='state',
)
st.altair_chart(chart, use_container_width=True)


