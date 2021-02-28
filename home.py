import streamlit as st
from PIL import Image


def app():
    st.title("Tobacco: a silent killer")
    
    st.markdown('''
    The Tobacco epidemic is considered one of the biggest public health threats by the World Health Organization (WHO). WHO estimates millions of deaths per year caused by the frequent use of Tobacco.

    However, WHO also states that Tobacco addiction is preventable and many measures are being applied to reduce its consumption as a world priority.
    ''')
    
    image = Image.open('img/smoking.jpg')

    st.image(image, caption='Image source: theconversation.com',
          use_column_width=True)
    
    st.header("Key facts")
    
    st.markdown('''
    * 20% of the world's population smoke tobacco everyday. WHO consider Tobacco as an epidemic
    * 7 million people a year die as a result of Smoking Tobacco (more than Covid-19)
    * Only 40% of the countries efficiently Monitor this issue.
    ''')
    
    st.header("Analysis Structure")
    
    st.markdown('''
                Now it's time to discover insights regarding this big threat "Tobacco" around three important questions:
    ''')
    
    image = Image.open('img/analysis.PNG')

    st.image(image, caption='',
          use_column_width=True)
          
          
    st.header("Team Members")
    
    st.markdown('''
      * Manh Hung Nguyen
      * Emir Nurmatbekov
      * Julio Candela
    ''')
    
    st.header("Sources")
    
    st.markdown('''
    * Tobacco Epidemic: https://www.who.int/news-room/fact-sheets/detail/tobacco#:~:text=Tobacco%20kills%20more%20than%208,-%20and%20middle-income%20countries.
    * Tobacco Consumption: http://ghdx.healthdata.org/record/ihme-data/global-smoking-prevalence-and-cigarette-consumption-1980-2012
    * Smoking Deaths: http://ghdx.healthdata.org/gbd-results-tool
    * Tobacco Control: https://apps.who.int/gho/data/node.main.Tobacco?lang=en
    ''')
