import home
import smoking_deaths
import tobacco_sales
import tobacco_control
import streamlit as st

PAGES = {
    "Homepage": home,
    "Tobacco Consumption": tobacco_sales,
    "Smoking Deaths": smoking_deaths,
    "Tobacco Control": tobacco_control,
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

