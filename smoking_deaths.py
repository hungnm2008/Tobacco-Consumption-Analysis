import altair as alt
import streamlit as st
import pandas as pd

def app():
    st.title("Smoking Deaths")
    st.header("Why Tobacco is a deadly threat?")
    
    @st.cache(allow_output_mutation=True)
    def load_data():
        deaths = pd.read_csv('data/smoking-deaths-by-age.csv',
                            header=0,
                            names=[
                                'country',
                                'code',
                                'year',
                                '15 to 49',
                                '50 to 69',
                                'Above 70'])

        factors = pd.read_csv('data/number-of-deaths-by-risk-factor.csv',
                            header=0,
                            index_col=False,
                            names=[
                                'country',
                                'code',
                                'year',
                                'Diet low in vegetables',
                                'Diet low in whole grains',
                                'Diet low in nuts and seeds',
                                'Diet low in calcium',
                                'Unsafe sex',
                                'No access to handwashing facility',
                                'Child wasting',
                                'Child stunting',
                                'Diet high in red meat',
                                'Diet low in fiber',
                                'Diet low in seafood omega-3 fatty acids',
                                'Diet high in sodium',
                                'Low physical activity',
                                'Non-exclusive breastfeeding',
                                'Discontinued breastfeeding',
                                'Iron deficiency',
                                'Vitamin A deficiency',
                                'Zinc deficiency',
                                'Smoking',
                                'Secondhand smoke',
                                'Alcohol use',
                                'Drug use',
                                'High fasting plasma glucose',
                                'High total cholesterol',
                                'High systolic blood pressure',
                                'High body-mass index',
                                'Low bone mineral density',
                                'Diet low in fruits',
                                'Diet low in legumes',
                                'Low birth weight for gestation',
                                'Unsafe water source',
                                'Unsafe sanitation',
                                'Household air pollution from solid fuels',
                                'Air pollution',
                                'Outdoor air pollution'])

        # Drop columns with missing values and extremely low values
        factors.drop(columns=['Vitamin A deficiency', 'High total cholesterol', 'Zinc deficiency', 'Child stunting', 'Discontinued breastfeeding',
                                'Iron deficiency', 'Non-exclusive breastfeeding','Diet high in red meat', 'Unsafe sanitation', 
                                'No access to handwashing facility','Household air pollution from solid fuels', 'Unsafe water source', 'Child wasting',
                                'Low birth weight for gestation', 'Diet low in calcium', 'Low bone mineral density',], inplace=True)

        # Filter data with years
        factors = factors.drop(factors[factors.year > 2012].index)
        deaths = deaths.drop(deaths[deaths.year > 2012].index)

        # Convert data from wide to long
        deaths = pd.melt(deaths, id_vars=['country', 'year'], value_vars=['15 to 49', '50 to 69', 'Above 70'], var_name='Age')
        factors = pd.melt(factors, id_vars=['country', 'year'], value_vars=['Diet low in vegetables',
                                'Diet low in nuts and seeds',
                                'Unsafe sex',
                                'Diet low in fiber',
                                'Diet low in seafood omega-3 fatty acids',
                                'Diet high in sodium',
                                'Low physical activity',
                                'Smoking',
                                'Secondhand smoke',
                                'Alcohol use',
                                'Drug use',
                                'High fasting plasma glucose',
                                'High systolic blood pressure',
                                'High body-mass index',
                                'Diet low in fruits',
                                'Diet low in legumes',
                                'Air pollution',
                                'Outdoor air pollution'], var_name='risk_factor')

        countries = deaths['country'].unique() # get unique country names
        countries.sort() # sort alphabetically
        minyear = deaths.loc[:, 'year'].min()
        maxyear = deaths.loc[:, 'year'].max()
        return deaths, factors, countries, minyear, maxyear

    # Load data
    deaths, factors, countries, minyear, maxyear = load_data()

    # Country Selection
    selectCountry = st.selectbox('Select a country: ', countries, 77)

    # Year selection
    slider = st.slider('Select a period of time', int(str(minyear)), int(str(maxyear)), (1994, 2004))

    # Bar chart - Risk factors
    bar_factors = alt.Chart(factors, title="Ranking of the top 10 risk factors leading to deaths in "
                 + selectCountry + " from " + str(slider[0]) + " to " + str(slider[1])).mark_bar().transform_filter({'and': [{'field': 'country', 'equal': selectCountry},
                                                                                                                            {'field': 'year', 'range': slider}]}
    ).transform_aggregate(
        sum_deaths='sum(value)', # Calculate the total number of deaths
        groupby=["risk_factor"]
    ).transform_window(
        rank='rank(sum_deaths)',
        sort=[alt.SortField('sum_deaths', order='descending')]
    ).transform_filter(
        alt.datum.rank < 11 # Filter out top 10 factors
    ).encode(
        alt.X('sum_deaths:Q', title='Total number of deaths'),
        y=alt.Y('risk_factor:O',sort='-x', title='Risk factor'),
        tooltip=alt.Tooltip(["sum_deaths:Q"],format=",.0f",title="Deaths"),
        color=alt.condition(
          alt.datum['risk_factor'] == 'Smoking',
          alt.value("red"),  # Color for the smoking factor
          alt.value("lightgray")  # Color for the rest
        )
    ).properties(
        width=660,
        height=300
    )
    
    # Stacked bar chart - Smoking deaths by ages
    base = alt.Chart(deaths, title='Smoking deaths by age in ' + selectCountry).mark_bar().transform_filter({'and': [{'field': 'country', 'equal': selectCountry},
                                                                                                                    {'field': 'year', 'range': slider}]}
    ).encode(
        alt.X('year:O', title='Year'),
        y=alt.Y('value:Q', title='Number of smoking deaths'),
        order=alt.Order('Age:O', sort='ascending'),
        color=alt.Color('Age:O',
                        scale = alt.Scale(domain=['Above 70', '50 to 69', '15 to 49'], scheme='lightorange')), 
        tooltip=alt.Tooltip(["value:Q"],format=",.0f",title="Deaths"),
    ).properties(
        width=720,
        height=300
    )

    
    # Render the charts
    container1 = st.beta_container()
    with container1:
        st.altair_chart(base)

    st.markdown("From the chart above we can see that smoking is a critical factor leading to deaths, especially for old people. The numbers of people aged over 70 who died because of smoking are extremely high in all countries. \
                In the bar chart below, we can see how smoking ranks in the list of top 10 risk factors that lead to deaths in the chosen country in the chosen period of time.")

    container2 = st.beta_container()
    with container2:
        st.altair_chart(bar_factors)

    