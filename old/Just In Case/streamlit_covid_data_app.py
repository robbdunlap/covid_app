# type "streamlit run streamlit_covid_data_app.py" at the command prompt to run

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import plotly.express as px

# title the page
st.title('COVID-19 Data by US State')
st.title('')   # padding to separate page title from graphs

# import data files
df = pd.read_csv("data/daily_cases_deaths.csv")
df_mob = pd.read_csv("data/all_state_mob_data.csv")

# rename mob_index columns to human readable names
df_mob = df_mob.rename(columns={"normal_exposure_per_day": "Normal", "strict_exposure_per_day": "Strict", "relaxed_exposure_per_day": "Relaxed"})

# convert the data data from object to datetime
df['Date'] = pd.to_datetime(df['Date'])
df_mob['Date'] = pd.to_datetime(df_mob['Date'])

# create df of mob data with just the three columns of interest
cols_to_keep = [2, 6, 37, 38, 39]
df_mob_indexes = df_mob.iloc[:, cols_to_keep]
df_mob_index_melt = pd.melt(df_mob_indexes, id_vars=['Date', 'sub_region_1'], value_vars=['Normal', 'Strict', 'Relaxed']).sort_values(by=['Date'])
df_mob_index_melt = df_mob_index_melt.rename(columns={"variable": "Posture"})

# grab a list of the states'/territories' names fromt the df so that streamlit can display a drop-down selector 
states = df.Province_State.unique()

# streamlit selectbox for selecting which state to plot
state_selected = st.sidebar.selectbox('Select state of interest', states, index=(46))

# subselect the data for the selected state from the dataframe
df_for_display = df[df.Province_State.isin([state_selected])]

df_mob_data_for_display = df_mob_index_melt[df_mob_index_melt.sub_region_1.isin([state_selected])]

# grab the latest date of the GCMD to let the user know how fresh the data is
gcmd_freshness = df_mob_data_for_display['Date'].max()
latest_date_of_goog_data = datetime.strftime(gcmd_freshness, '%Y-%m-%d')

#==============================================================
# Create dual-axis plot to display 7-day rolling average of new_cases and new_deaths for the state selected
#==============================================================

# first, create a scalling factor so the daily_deaths_rollavg will "fit under" the daily_cases_rollavg line
###   grab max value of each column 
all_scale = df_for_display.max()

print(df_for_display.head(3))

###   subselect the max values for new_cases_daily and new_deaths_daily 
latest_date_of_data = datetime.strftime(all_scale[1], '%Y-%m-%d')
new_cases_max = all_scale[3]
new_deaths_max = all_scale[5]


###   change this number to adjust the scale of the secondary Y-axis so the the daily_new_deaths
###   smaller than the new_cases_daily
set_scale_factor = 3

###   calculate the scale adjustment for the seondary Y-axis and return it as a list for altair to graph
scale_factor = int(new_deaths_max * set_scale_factor)
for_scaling = [0, scale_factor]

# show latest date of data on the dashboard
for i in range(1,11):     # padding
    st.sidebar.title('')   
st.sidebar.markdown(f'##### Data is from JHU dataset with {latest_date_of_data} being the latest date of data in the set')
st.sidebar.markdown('##### https://github.com/CSSEGISandData/COVID-19') 
st.sidebar.title('')       # padding 
st.sidebar.markdown(f'##### Mobility index is derived from Google Mobility Data as of {latest_date_of_goog_data}')
st.sidebar.markdown('##### https://www.google.com/covid19/mobility/index.html')

#=======================================================
# chart plotting (altair chart that streamlit natively publishes)
#=======================================================

# graph title
cases_deaths_graph_title = 'Rolling 7-day Average of New Cases and Deaths per Day in ' + state_selected

base = alt.Chart(df_for_display).encode(
    alt.X('Date:T', axis=alt.Axis(title='Date'))).properties(
        title=cases_deaths_graph_title
    )

cases = base.mark_area(color='#858ce6').encode(
    alt.Y('new_cases_rollavg:Q', 
    axis=alt.Axis(title='7-day Rolling Avg of New Cases', titleColor='#858ce6'))
)

deaths = base.mark_area(color='#9c2927').encode(
    alt.Y('new_deaths_rollavg:Q', 
    axis=alt.Axis(title='7-day Rolling Avg of New Deaths', titleColor='#9c2927'),
    scale=alt.Scale(domain=for_scaling))
)

new = alt.layer(cases, deaths).resolve_scale(y='independent').configure_axisLeft(labelColor='#858ce6').configure_axisRight(labelColor='#9c2927')

st.altair_chart(new, use_container_width=True)


# exposure index plots
# https://github.com/altair-viz/altair/issues/968 - states use of long vs. wide form data is better and link to Altair explanation


mob_chart = alt.Chart(df_mob_data_for_display).mark_line().encode(
    x='Date',
    y='value',
    color='Posture'
).properties(
        title='Hypothetical Daily Exposure Index Based on Mobility and Non-pharmaceutical Interventions'
    )
st.altair_chart(mob_chart, use_container_width=True)



# example for plotting CDC excess deaths vs JHU reported deaths and correlation scatter chart of same
# save this to use on a separate streamlit page (if necessary) for state level statistics 

# plotting_reported_deaths = weekly_cases_deaths_xs[(weekly_cases_deaths_xs['state'] == state_selected)]

# fig = px.bar(plotting_reported_deaths, 
#              x="date", 
#              y=["Excess Lower Estimate", "Excess Higher Estimate","new_deaths_jhu"], 
#              barmode='group',
#              title = f"Reported and Excess Deaths in {state_selected}")
# fig.update_yaxes(title_text='Deaths')
# st.plotly_chart(fig)

# fig2 = px.scatter(plotting_reported_deaths, x='new_deaths_jhu', y=['Excess Lower Estimate','Excess Higher Estimate'], trendline='ols')
# fig2.update_layout(title=state_selected)
# fig2.update_yaxes(title_text='Mid Point Estimate of Excess Deaths')
# fig2.update_xaxes(title_text='JHU Reported Deaths')
# st.plotly_chart(fig2)




df_est_cases = pd.read_csv("data/weekly_est_cases_deaths.csv")
df_for_display2 = df_est_cases[df_est_cases.state.isin([state_selected])]
df_for_display3 = df_for_display2[['date', 'new_cases_jhu', 'est_inf']].copy()
df_for_display3.rename(columns={'date':'Week','new_cases_jhu':'JHU Reported','est_inf':'Est Actual Inf'}, inplace=True)

fig3 = px.bar(df_for_display3, 
             x="Week", 
             y=["JHU Reported", "Est Actual Inf"], 
             barmode='group',
             title = f"Reported and Estimated New Cases in {state_selected}",
             hover_name='Week')
fig3.update_yaxes(title_text='New Cases')
fig3.update_xaxes(showgrid=True)
fig3.update_layout(
    xaxis_tickformat = '%b<br>%Y')

st.plotly_chart(fig3, use_container_width=True)


# df_for_display4 = df_for_display3.copy()
# df_for_display4.melt('Week', var_name='Source', value_name='Infections')


# base = alt.Chart(df_for_display3).encode(
#     x = 'Week:T', 
#     y = 'Infections',
#     color = 'Source'
# )

# st.altair_chart(base, use_container_width=True)






# base = alt.Chart(df_for_display3).transform_fold(
#     ['JHU Reported', 'Est Actual Inf'],
#     as_=['info source', 'infections']
# ).mark_bar(opacity=0.5).encode(
#     x='Week:T',
#     y=alt.Y('infections:Q', stack=None),
#     color='info source:N'
# )
# st.altair_chart(base, use_container_width=True)



##### reported and estimated cases that occured in the selected state - need to select the data
# fig = px.bar(plotting_reported_deaths, x="date", y=["new_deaths_jhu", "corr_new_deaths"], 
#              barmode='group',
#              title = f"Reported and Estimated Deaths in {state_selected}")
# fig.show()