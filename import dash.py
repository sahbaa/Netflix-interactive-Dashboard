import dash
from dash import Input,Output
from dash import html,dcc
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
from dash_bootstrap_templates import ThemeSwitchAIO , template_from_url

# READ data 
#===================
df = pd.read_csv('netflix1.csv')

# Define Theme
#===================
url_theme1 = dbc.themes.SKETCHY
url_theme2 = dbc.themes.SLATE
bootstrapTheme = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"

# Create app (dashComponent )
# #=================== 
app = dash.Dash(__name__,title='Netflix',external_stylesheets=[url_theme1,bootstrapTheme])


# Define the Layout
#===================
app.layout = dbc.Container([

                dbc.Row([
                    dbc.Col([html.H1('Netflix Analytics Dashboard'),
                            ThemeSwitchAIO(aio_id='themeswithcer',themes=[url_theme1, url_theme2])
                             
                             ]),
                    
                    dbc.Col([
                       dbc.Card([dbc.CardBody([
                            html.H5('🎞 Total Titles',className='Card_title'),
                            html.H2( id= 'total' ,className='Card_Total_Number' )
                       ])]) 
                    ],width=3),
                    dbc.Col([
                        dbc.Card([dbc.CardBody([
                            html.H5('🌍 Top Country',className='Title_Country'),
                            html.H2(id='best_country', className='Card_bestCountry')
                        ])])
                    ],width=3),
                    dbc.Col([
                        dbc.Card([dbc.CardBody([
                            html.H5('🎭 Top Genre' , className='Card_genre'),
                            html.H2(id = 'bestGenre' , className= 'Card_bestGenre')                    
                                                ])])
                    ],style={'marginBottom': '20px'},width=3)
                    ])
                ,
   
                dbc.Row([
                    dbc.Col([
                        html.H5('select the range of the year!'),
                        dcc.RangeSlider(id='sliderYear',min=df['release_year'].min() , max=df['release_year'].max(),
                                    marks={year: str(year) for year in sorted(df['release_year'].unique())[::2]},  # label every year
                                    value=[2015,2022], tooltip={"always_visible": True},step=None)],width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(id='inp_pie',options=[{ 'label':i,'value':i } for i in  ['type','rating']]
                            ,value='type'),

                        dcc.Graph(id = 'pie',figure={})                  
                    ],width=6),

                    dbc.Col([dcc.Dropdown(id='inp_bar',options=[{ 'label':i,'value':i } for i in ['type','release_year','listed_in']],value='type'
                                          ),
                                      dcc.Graph(id='bar',figure={})],width=6)
                ])            
                ,
                dbc.Row([dbc.Col([
                    html.H5('here is the number of movie in each country'),
                    dcc.Graph(id='choropleth',figure={})
                ])]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id = 'lineChart' , figure= {})
                    ])
                ]),
                dbc.Row([
                    dbc.Col([dcc.Graph(id = 'gphist', figure = {})])
                ])

])


# specify the role of inputs and outputs
#===================
@app.callback(
        [
        Output(component_id='total', component_property='children'),
        Output(component_id='best_country',component_property='children'),
        Output(component_id='bestGenre',component_property='children'),
        Output(component_id='pie',component_property='figure'),
        Output(component_id='bar',component_property='figure'),
        Output(component_id='choropleth',component_property='figure'),
        Output(component_id='lineChart',component_property='figure'),
        Output(component_id='gphist',component_property='figure')
        
        ],

        [Input(ThemeSwitchAIO.ids.switch("themeswithcer"),"value"),
         Input(component_id='inp_pie',component_property='value'),
         Input(component_id='inp_bar',component_property='value'),
         Input(component_id='sliderYear',component_property='value') 
        ]
)

# make relation between input and output
#===================
def result(tgl , pieinp,barinp,slider):

    # Setting Up Theme:
    #===================
    tem = template_from_url(url_theme1 if tgl else url_theme2)
    # plot
    #====================   
    # make ready data for plotting
    #====================
    dff = df[(df['release_year'] >= slider[0]) & (df['release_year'] <= slider[1])].copy() 
    activest = dff.copy()

    # First output(total number of data specified in the slider range)
    #====================
    total = len(dff)

    # Second output (the best country in quantity of production)
    #====================
    activest['country'] = dff['country'].str.split(',')
    activest = activest.explode('country')
    activest['country'] = activest['country'].str.strip()
    activest = activest.groupby('country').size().reset_index(name = 'count')
    bestcntry = activest.sort_values('count',ascending = False).iloc[0]['country']

    # Third output (best Genre which is produced by considering the year range)
    #====================
    bestGenre = dff.copy()
    bestGenre['listed_in'] = bestGenre['listed_in'].str.split(',')
    bestGenre = bestGenre.explode('listed_in')
    bestGenre['listed_in'] = bestGenre['listed_in'].str.strip()
    bestGenre = bestGenre.groupby('listed_in').size().reset_index(name = 'count')
    bestGenre2 = bestGenre.sort_values('count',ascending = False).iloc[0]['listed_in']

    # producing the Pie chart according to the filed which is selected in dropdown
    #====================
    df_for_pie = dff[pieinp].value_counts().reset_index() 
    df_for_pie.columns = ['name','value']
    fig1 = px.pie(df_for_pie, names='name',values='value', title=f"{pieinp} Distribution",template=tem)

    # plotting barplot by considering the filed which is selected from dropdown list:
    #====================
    df_for_bar = dff[barinp].value_counts().reset_index()
    df_for_bar.columns = ['categories','countOfeachCategory']
    fig2 = px.bar(data_frame=df_for_bar,x= 'categories',y='countOfeachCategory',title=f"{barinp} BarGraph",template=tem,color_discrete_sequence=['#b72d2d', '#c5355e', '#9b878a'])

    #plotting choropleth map in order to find the trend of changing in number of the contents which is produced along the years
    #====================
    df_for_choropleth = dff.copy()
    df_for_choropleth['country'] = df_for_choropleth['country'].str.split(',')
    df_for_choropleth = df_for_choropleth.explode('country')
    df_for_choropleth['country'] = df_for_choropleth['country'].str.strip()
    df_for_choropleth = df_for_choropleth.groupby(['release_year','country']).size().reset_index(name='count') 
    fig3 = px.choropleth(df_for_choropleth,
                        locations='country',  # This column contains state abbreviations (e.g., 'TX' for Texas)
                        color='count',
                        animation_frame='release_year',
                        title='choropleth Map',
                        locationmode='country names',
                        template= tem,
                        color_continuous_scale= 'RdBu')
    
    # plotting line chart (constant chart) to show how number of contents are changed over the time
    #====================
    df_for_lineChart = df.copy()
    df_for_lineChart = df_for_lineChart.groupby(['release_year']).size().reset_index(name='count')
    fig4 = px.line(df_for_lineChart,x='release_year',y = 'count',template=tem)
    fig4.update_layout(
    yaxis=dict(
        range=[0, 1200],
        tick0=0,
        dtick=50))

    # plotting barchart in order to find the changing the quantity of productions over the time by considering Movie or Series:
    #====================
    df_for_gplineChart = df.groupby(['release_year','type']).size().reset_index(name='count')
    fig5 = px.histogram(df_for_gplineChart,x = 'release_year',barmode='group',color = 'type',template=tem)
    fig5.update_layout(yaxis=dict(range=[0,15]))

    return total,bestcntry,bestGenre2,fig1,fig2,fig3,fig4,fig5

if __name__ == '__main__':
    app.run_server(debug=True)