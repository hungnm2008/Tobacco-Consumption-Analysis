import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

CHART_HEIGHT = 200
CHART_WIDTH = 500

def app():
    @st.cache
    def load_data(smokers_path, consumption_path):
        smokers_data = pd.read_csv(smokers_path,
                            header=0,
                            names=[
                                'Country',
                                'Code',
                                'Year',
                                'NumCig'
                            ],
                            dtype={'Country': str,
                                    'Code': str,
                                    'Year': 'Int64',
                                    'NumCig': 'float64'})
        consumption_data = pd.read_csv(consumption_path,
                            header=0,
                            names=[
                                'Country',
                                'Code',
                                'Year',
                                'NumCig'
                            ],
                            dtype={'Country': str,
                                    'Code': str,
                                    'Year': 'Int64',
                                    'NumCig': 'float64'}
                            )
        return smokers_data, consumption_data

    smokers_path = 'data/daily-smoking-prevalence-bounds.csv'
    consumption_path = 'data/consumption-per-smoker-per-day.csv'
    smokers_data, consumption_data = load_data(smokers_path, consumption_path)
    container = st.beta_container()
    with container:
        # st.header('Tobacco smokers trend in different countries')
        st.title("Tobacco consumption")
        countries = st.multiselect('Select countries to plot',
                            smokers_data.groupby('Country').count().reset_index()['Country'].tolist(),
                            default=['France', 'Germany', 'Spain'])

    # lower year bound
    min_year_smokers = max(smokers_data.loc[smokers_data['Country'] == country]['Year'].min()
    for country in countries)
    min_year_consumption = max(consumption_data.loc[consumption_data['Country'] == country]['Year'].min()
    for country in countries)
    min_year = max(min_year_smokers, min_year_consumption)

    # upper year bound
    max_year_smokers = min(smokers_data.loc[smokers_data['Country'] == country]['Year'].max()
    for country in countries)
    max_year_consumption = min(smokers_data.loc[smokers_data['Country'] == country]['Year'].max()
    for country in countries)
    max_year = min(max_year_smokers, max_year_consumption)

    with container:
        slider = st.slider('Select a period to plot',
                        int(str(min_year)), 
                        int(str(max_year)),
                        (int(str(min_year)), 2010))
                        
    smokers_chart = alt.Chart(smokers_data, height=CHART_HEIGHT, width=CHART_WIDTH,
                            title='Share of adults who smoke every day(%)',
                            ).mark_line().encode(
                            alt.X('Year', axis=alt.Axis(title='Years', tickCount=5)),
                            alt.Y('NumCig', axis=alt.Axis(title='')),
                            alt.Color('Country', legend=alt.Legend(orient='top'))
                            ).transform_filter(
                                                {'and': [{'field': 'Country', 'oneOf': countries},
                                                        {'field': 'Year', 'range': slider}]}
                                                )
    consumption_chart = alt.Chart(consumption_data, height=CHART_HEIGHT, width=CHART_WIDTH,
                                    title='Consumption per smoker per day').mark_line().encode(
                                        alt.X('Year', axis=alt.Axis(title='Years', tickCount=5)),
                                        alt.Y('NumCig', axis=alt.Axis(title='')),
                                        alt.Color('Country', legend=alt.Legend(orient='top'))
                                        ).transform_filter(
                                            {'and': [{'field': 'Country', 'oneOf': countries},
                                                    {'field': 'Year', 'range': slider}]}
                                            )

    # ruler
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['Year'], empty='none')
    smokers_selectors = alt.Chart(smokers_data).mark_point().encode(
        x='Year:Q',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    ).transform_filter({'and': [{'field': 'Country', 'oneOf': countries},
                {'field': 'Year', 'range': slider}]})
    smokers_points = smokers_chart.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    smokers_text = smokers_chart.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'NumCig:Q', alt.value(' '), format='.1f')
    )
    smokers_rules = alt.Chart(smokers_data).mark_rule(color='gray').encode(
        x='Year:Q',
    ).transform_filter(
        nearest
    )

    consumption_selectors = alt.Chart(consumption_data).mark_point().encode(
        x='Year:Q',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    ).transform_filter({'and': [{'field': 'Country', 'oneOf': countries},
                {'field': 'Year', 'range': slider}]})
    consumption_points = consumption_chart.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    consumption_text = consumption_chart.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'NumCig:Q', alt.value(' '), format='.1f')
    )
    consumption_rules = alt.Chart(consumption_data).mark_rule(color='gray').encode(
        x='Year:Q',
    ).transform_filter(
        nearest
    )



    with container:

        
        smokers_chart = alt.layer(
        smokers_chart, smokers_selectors, smokers_points, smokers_rules, smokers_text
        )
        consumption_chart = alt.layer(
        consumption_chart, consumption_selectors, consumption_points, consumption_rules, consumption_text
        )
        st.altair_chart(alt.vconcat(smokers_chart, consumption_chart))
       	st.markdown(
        '''
        Above, you can see how share of smokers and consumption of cigarettes changed over the years in different countries.
        The share of smokers chart shows the percentage of every-day-smoking adults, the consumption chart
        displays the average number of cigarettes consumed daily per smoker.
        Use the year slider to choose a period to focus on and also select the countries of your interest.
        '''
        )


app()