import streamlit as st
import pandas as pd
import altair as alt
import json
import requests
import numpy as np
from IPython.display import display, HTML
from altair import datum
import matplotlib.pyplot as plt
from io import BytesIO

def app():

    ####### Datasets
    
    control_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/control_policy.csv'
    deaths_dataset = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/data/deaths.csv'
    
    
    ####### Dataframes
    
    control_df = pd.read_csv(control_dataset)
    
    
    ####### Dashboard
    
    st.title("Tobacco Control")
    
    
    
    
    st.markdown('''
    The following analysis is based on the evaluation made by World Health Organization (WHO) 
    to country policies against Tobacco. A score from 1 to 5 is assigned depending on the intensity 
    of a country to deal with Tobacco issues being 1 the worst and 5 the best
    ''')
    
    ####### Control Measures given by WHO
    
    control_metrics = ["Monitor",	
               "Protect from tobacco smoke",	
               "Offer help to quit tobacco use", 
               "Warn about the dangers of tobacco",
               "Enforce bans on tobacco advertising",
               "Raise taxes on tobacco",
               #"Anti-tobacco mass media campaigns"
    ]
    
    
    # Main Selector of Control Measures
    cols = st.selectbox('Select control measure: ', control_metrics)
    
    if cols in control_metrics:   
        metric_to_show_in_covid_Layer = cols +":Q"
        metric_name = cols
       
    years = ['2008', '2010', '2012', '2014', '2016', '2018']
    columns_year = [metric_name+" "+str(year) for year in years]
    columns = ["d" +str(year) for year in years]
        
        
    container_map = st.beta_container()
    
    
    ####### Map Visualization
    
    with container_map:
        
        st.header("How are countries controlling Tobacco consumption?")
        #st.header('"'A global view of the implementation of the policy """ around the world'"')
    
        st.markdown('''
        In the folling map, we can identify the intensity of a specific control policy for each country. 
        We can also see the evolution of these policies from 2008 to 2018
        ''')
        
        # Year Selector
        select_year_list = st.selectbox('Select year: ', years)#st.slider('Select year: ', 2008, 2018, 2008, step = 2)
        select_year = int(select_year_list)

        # Map Topology
        url_topojson = 'https://raw.githubusercontent.com/JulioCandela1993/VisualAnalytics/master/world-countries.json'
        data_topojson_remote = alt.topo_feature(url=url_topojson, feature='countries1')
        
        
        ### Map Chart
        
        map_geojson = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke="black",
            strokeWidth=1,
            #fill='lightgray'
        ).encode(
            color=alt.Color(metric_to_show_in_covid_Layer),
        ).transform_lookup(
                lookup="properties.name",
                from_=alt.LookupData(control_dataset, "Country", [metric_name,"Year"])
        ).properties(
            width=700,
            height=500
        )
              
        choro = alt.Chart(data_topojson_remote, title = 'Implementation of the policy "' +metric_name+'" around the world').mark_geoshape(
            stroke='black'
        ).encode(
            color=alt.Color(metric_to_show_in_covid_Layer, 
                            scale=alt.Scale(range=['#ffe8dd','#ef4f4f']),
                            legend=None),
            tooltip=[
                alt.Tooltip("properties.name:O", title="Country"),
                alt.Tooltip(metric_to_show_in_covid_Layer, title=metric_name),
                alt.Tooltip("year:Q", title="Year"),
            ],
        ).transform_calculate(
            d2008 = "1",
            d2010 = "1",
            d2012 = "1",
            d2014 = "1",
            d2016 = "1",
            d2018 = "1"
        ).transform_fold(
            columns, as_=['year', 'metric']
        ).transform_calculate(
            yearQ = 'replace(datum.year,"d","")'
        ).transform_calculate(
            key_val = 'datum.properties.name + datum.yearQ'
        ).transform_lookup(
                lookup="key_val",
                from_=alt.LookupData(control_dataset, "ID", [metric_name,"Year"])
        ).transform_calculate(
            year='parseInt(datum.Year)',
        ).transform_filter(
            alt.FieldEqualPredicate(field='year', equal=select_year)
        )
    
    
        st.altair_chart(map_geojson + choro)
            
        ## Qualification array
        
        qualifications = pd.DataFrame.from_dict({
            "keys": [1,2,3,4,5],
            "category":["1.Very Bad", "2.Bad", "3.Medium", "4.Good", "5.Perfect"]
            })
        
        ## Legend Chart
        
        ##### Data Transformations

        legend_info = alt.Chart(control_dataset).transform_joinaggregate(
            num_countries='count(*)',
        ).transform_filter(
            alt.FieldEqualPredicate(field='Year', equal=select_year)
        ).transform_lookup(
                lookup=metric_name,
                from_=alt.LookupData(qualifications, "keys", ["category"])
        ).transform_aggregate(
            count='count()',
            groupby=[metric_name,"category"]
        ).transform_joinaggregate(
            total='sum(count)'  
        ).transform_calculate(
            pct='datum.count / datum.total'  
        )
        
        legend_bar = legend_info.mark_bar().encode(
                x=alt.X('pct:Q', stack="normalize", sort=alt.SortField(metric_to_show_in_covid_Layer), title = None, axis = None),                
                color=alt.Color(metric_to_show_in_covid_Layer,
                            scale=alt.Scale(range=['#ffe8dd','#ef4f4f'])
                            ,legend = None),
                tooltip=[
                    alt.Tooltip(metric_to_show_in_covid_Layer, title=metric_name)
                ],
        )
        
        legend_value = legend_info.mark_text(dx = -11, align='center', baseline='middle', color='black', fontWeight = "bold").encode(
            x=alt.X('pct:Q', sort=alt.SortField(metric_to_show_in_covid_Layer), stack='normalize', axis = None),
            #detail = metric_to_show_in_covid_Layer,
            color=alt.Color(metric_name +":O",
                            scale=alt.Scale(range=['#000000','#000000'])
                            ,legend = None),
            text=alt.Text('pct:Q',format='.0%')
        )
        
        legend_category = legend_info.mark_text(dx = 10, dy = 10, align='left', baseline='middle', color='black', angle = 90, fontWeight = "bold").encode(
            x=alt.X('pct:Q', sort=alt.SortField(metric_to_show_in_covid_Layer), stack='normalize', axis = None),
            #detail = metric_to_show_in_covid_Layer,
            color=alt.Color(metric_name +":O",
                            scale=alt.Scale(range=['#000000','#000000'])
                            ,legend = None),
            #text=alt.Text(metric_to_show_in_covid_Layer)
            text=alt.Text("category:N")
        )
            
        legend_chart = (legend_bar + legend_value + legend_category).properties(
            width=700,
            height=100,
            title = metric_name
        ).configure_title(align = "left"
        ).configure_view(
            strokeWidth=0
        )
        
        
        st.altair_chart(legend_chart)
        
    ##### Evolution of policy per selected countries    
        
    container_policycountry = st.beta_container()
    with container_policycountry:   
        
        st.header("Evolution of the policy per country")
        
        
        st.markdown('''
        
        In addition, we can evaluate and compare the evolution of the selected policy among different countries of our interest:
        
        ''')
    
    
        ## Selector of countries
        
        countries = st.multiselect('Select countries to plot',
                                    control_df.groupby('Country').count().reset_index()['Country'].tolist(),
                                    default=['China', 'India', 'France'])
        
        st.markdown('''
        
    
        ''') 
        
        xscale_barchart = alt.Scale(domain=(0, 5))
        
        ## Comparisson Chart of Policies per country
        
        barchart_country = alt.Chart(control_dataset,width=90,height=20,
                                     title = 'Evolution of Policy "' + metric_name + '" per selected countries'
        ).mark_bar( size = 20
        ).encode(
            alt.X('value:Q', scale = xscale_barchart, title = "", axis = alt.Axis(grid = False)),
            alt.Row('Country:N', title = "", spacing = 5, header = alt.Header(labelAngle = 0, labelAlign = "left",labelLimit = 100)),
            alt.Column("Year:O", title = "", spacing = 10),
            color=alt.Color("value:Q", 
                            scale=alt.Scale(domain=[1,4], range=['#ffe8dd','#ef4f4f']),
                            legend=None),
            tooltip=[
                alt.Tooltip("Country:N", title="Country"),
                alt.Tooltip(metric_to_show_in_covid_Layer, title=metric_name),
                alt.Tooltip("Year:O", title="Year"),
            ]
        ).transform_fold(
            [metric_name],
            as_ = ['Measurement_type', 'value']
        ).transform_filter(
            alt.FieldOneOfPredicate(field="Country", oneOf=countries)
        ).transform_filter(
            {'field': 'Year', 'range': [2008,2018]}
        ).configure_title(align = "center", anchor = "middle", dy = -10)
            
            
        st.altair_chart(barchart_country)
        
        st.altair_chart(legend_chart)
        
    
    ####### Scatterplot control policy vs deaths
    
    def render_latex(formula, fontsize=10, dpi=100):
        """Renders LaTeX formula into Streamlit."""
        fig = plt.figure()
        text = fig.text(0, 0, '$%s$' % formula, fontsize=fontsize)
    
        fig.savefig(BytesIO(), dpi=dpi)  # triggers rendering
    
        bbox = text.get_window_extent()
        width, height = bbox.size / float(dpi) + 0.05
        fig.set_size_inches((width, height))
    
        dy = (bbox.ymin / float(dpi)) / height
        text.set_position((0, -dy))
    
        buffer = BytesIO()
        fig.savefig(buffer, dpi=dpi, format='jpg')
        plt.close(fig)
    
        st.image(buffer)
    
    
    
    container_correlation = st.beta_container()
    with container_correlation: 
    
        st.header("Are the policies having an impact in the deaths by Smoking?")
        
        st.markdown('''
        Countries have implemented different control policies against Tobacco which have been measured by WHO from 2008 until 2018. 
        During this period, some countries have strengthen their policies; however, we don't know the real impact of them.
        
        As a consequence, the following visualization measures the correlation of the change in control policies with 
        respect to the change in deaths by Smoking. The definitions of % of change are the following:
            
        ''')    
        
        render_latex(r'\%\ change\ in\ '+metric_name+r'\ =\ \frac{'+metric_name+r'\ in\ 2016}{'+metric_name+r'\ in\ 2008}')
        
        render_latex(r'\%\ change\ in\ Deaths\ by\ Smoking\ =\ \frac{Deaths\ by\ Smoking\ in\ 2016}{Deaths\ by\ Smoking\ in\ 2008}')
        
        st.markdown('''
        The user can also select brush the histograms in order to filter the points and 
        evaluate the slope of the regression in more detail (with groups that increased more or less in control policies, for example)
        
        
        ''')
    
        brush = alt.selection_interval()
        
        ## Data Transformations
        
        base_scatter = alt.Chart(control_dataset).transform_lookup(
                lookup="ID",
                from_=alt.LookupData(deaths_dataset, "ID", ["deaths","Year"])
        ).transform_calculate(
            deaths='parseFloat(datum.deaths)',
            year='parseInt(datum.Year)',
            metric = alt.datum[metric_name]
        ).transform_calculate(
            deaths_2016='datum.year==2016?datum.deaths:0',
            deaths_2008='datum.year==2008?datum.deaths:0',
            metric_2016='datum.year==2016?datum.metric:0',
            metric_2008='datum.year==2008?datum.metric:0',
            year='parseInt(datum.Year)',
            sizepoint = '2'
        ).transform_aggregate(
            deaths_2016='sum(deaths_2016)',
            metric_2016='sum(metric_2016)',
            deaths_2008='sum(deaths_2008)',
            metric_2008='sum(metric_2008)',
            groupby=["Country"]
        ).transform_calculate(
            incr_ratio_deaths='((datum.deaths_2016/datum.deaths_2008)-1)*100',
            incr_ratio_metric='((datum.metric_2016/datum.metric_2008)-1)*100',
        )
        
        xscale = alt.Scale(domain=(-100, 300))
        yscale = alt.Scale(domain=(-100, 200))
        
        
        ## Scatterplot of changes in Policy and changes in deaths
        
        points_scatter = base_scatter.mark_point(size=50, stroke="#ef4f4f").encode(
            alt.X('incr_ratio_metric:Q', scale = xscale, title = '% change of efforts in ' + metric_name + ' from 2008 to 2016'),
            alt.Y('incr_ratio_deaths:Q', scale=yscale, title = '% change in deaths from 2008 to 2016'),
            #color=alt.condition(brush, alt.value('blue'), alt.value('lightgray')),  
            #opacity=alt.condition(brush, alt.value(0.75), alt.value(0.05)),
            tooltip=[
                        alt.Tooltip("deaths_2016:Q", title="Deaths in 2016"),
                        alt.Tooltip("deaths_2008:Q", title="Deaths in 2008"),
                        alt.Tooltip("Country:N", title="Country"),
                    ],
        ).properties(
            width=450,
            height=450
        ).transform_filter(brush)   
            
        regression_scatter = points_scatter.transform_regression(
                on='incr_ratio_metric', regression='incr_ratio_deaths', method = 'linear'
        ).mark_line(color='#19456b')
        
        scatter_final = (points_scatter + regression_scatter)
           
        # Histogram of changes in policy
        
        top_hist = base_scatter.mark_area(line=True, opacity=0.3).encode(
            alt.X("incr_ratio_metric:Q",
                  bin=alt.Bin(maxbins=30, extent=xscale.domain),
                  title=''
                  ),
            alt.Y('count()', title=''),
            color=alt.value("#ef4f4f")
        ).add_selection(
            brush
        ).properties(width=450 , height=100, title = "Distribution of % change in policy")
        
        # Histogram of changes in deaths    
            
        right_hist = base_scatter.mark_area(line=True, opacity=0.3).encode(
            alt.Y('incr_ratio_deaths:Q',
                  bin=alt.Bin(maxbins=20, extent=yscale.domain),
                  title='',
                  ),
            alt.X('count()', title=''),
            color=alt.value("#ef4f4f")
        ).add_selection(
            brush
        ).properties(width=110, height=450, 
                     title=alt.TitleParams(text="Distribution of % change in deaths", align="center", angle = 90, orient = 'right')
        )
        
        st.altair_chart((top_hist & (scatter_final |right_hist )
            ).properties(title = "Correlation between % change in policy and % change in deaths"
            ).configure_title(align = "center", anchor = "middle", dy = -10))


                         
                         
                         
#app()



   
  
    
 