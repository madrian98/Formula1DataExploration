#!/usr/bin/env python
# coding: utf-8

# # Formula 1 (1950-2022) World Championship Data Exploration

# # 1.Introduction

# ## 1.1 About Formula 1
# Formula One (a.k.a. F1)  is an international auto racing sport. It is the highest level of single-seat, open-wheel and open-cockpit professional motor racing contest and is is governed and sanctioned by a world body called the FIA − Fédération Internationale de l'Automobile(FIA).The name ‘Formula’ comes from the set of rules that the participating cars and drivers must follow.F1 season consists of a series of races, known as Grands Prix, which take place worldwide on purpose-built circuits and on public roads.
# 

# ## 1.2 Setup
# 

# ### Project setup

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
import folium
import ipywidgets as widgets
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from IPython.display import display, HTML
pyo.init_notebook_mode()

display(HTML("<style>.container { width:100% !important; }</style>"))

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', 50)
warnings.filterwarnings("ignore")


# ## 1.3 Datasets

# ### About Dataset

# The dataset consists of all information on the Formula 1 such as races, drivers, constructors, qualifying, circuits, lap times, pit stops, championships etc.  from 1950 till the end of 2022 season.<br />
# Full dataset is available at http://ergast.com/mrd/.

# ### Reading data

# In[2]:


#Reading all data sets
data_url="https://github.com/madrian98/Formula1DataExploration/blob/main/Data"
data_raw="?raw=true"
races = pd.read_csv((data_url+"/races.csv"+data_raw))
drivers = pd.read_csv((data_url+"/drivers.csv"+data_raw))
constructors = pd.read_csv((data_url+"/constructors.csv"+data_raw))
results = pd.read_csv((data_url+"/results.csv"+data_raw))
circuits = pd.read_csv((data_url+"/circuits.csv"+data_raw))


# ### Data information

# In[3]:


#Races
races.info()
#Drivers
drivers.info()
#Constructors
constructors.info()
#Results
results.info()
#Circuits
circuits.info()


# ## 1.4 Data pre-processing

# In[4]:


#joining results on drivers on driverID(inner join)
dfDriver_res = pd.merge(results,drivers,on='driverId')
#joining previously created table on races by raceID(inner join)
dfConstructor_res = pd.merge(dfDriver_res,races,on='raceId')
#joining previously created table on constructors by constructorID(inner join)
dfRaceResults = pd.merge(dfConstructor_res,constructors,on='constructorId')
#Creating driver full name column
dfRaceResults['full_name'] = dfRaceResults['forename'] + ' ' + dfRaceResults['surname']
#Removing unnecessary columns
dfRaceResults = dfRaceResults.drop(columns=['url_x','url_y','name_y','nationality_y','url','time_y','fp1_date','fp1_time','fp2_date','fp2_time','fp3_date','fp3_time','quali_date','sprint_date','sprint_time'])
#Display data
dfRaceResults.head(5)


# # 2.General Statistics

# ## 2.1 About F1 circuits,drivers and constructors

# In[5]:


#Circuits
df_circuits = circuits.groupby('country').agg({'name':'count'}).reset_index()
df_circuits.rename({'name':'circuits_count'},axis=1,inplace=True)
#Drivers
df_drivers = drivers.groupby('nationality').agg({'driverRef':'count'}).reset_index()
df_drivers = df_drivers.rename({'driverRef':'driver_count'},axis=1)
#Constructors
df_constructors = constructors.groupby('nationality').agg({'constructorRef':'count'}).reset_index()
df_constructors = df_constructors.rename({'constructorRef':'constructors_count'},axis=1)


# In[6]:


df1=df_circuits.sort_values('circuits_count',ascending=True)
df2=df_drivers.sort_values('driver_count',ascending=True)
df3=df_constructors.sort_values('constructors_count',ascending=True)





from plotly.subplots import make_subplots


fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Total circuits per country', 'Total drivers per country','Total constructors per country'),
    horizontal_spacing = 0.1,
    vertical_spacing = 0.5)

fig.add_trace(go.Bar(
                x=df1['circuits_count'],
                y=df1["country"],
                hovertext='Circuits',
                orientation='h'),
                row=1, col=1)

fig.add_trace(go.Bar(
                x=df2['driver_count'],
                y=df2["nationality"],
                hovertext='Drivers',
                orientation='h'),
                row=1, col=2)

fig.add_trace(go.Bar(
                x=df3['constructors_count'],
                y=df3["nationality"],
                hovertext='Constructors',
                orientation='h'),
                row=1, col=3)
fig.update_layout(title_text='<b> F1 countries information [Circuits,Drivers,Constructors]<b>', 
                  titlefont={'size':25},
                  title_x=0.33,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template='ggplot2',
                  paper_bgcolor='orange'
                 )

fig.show()


# ### Circuits location on world map

# In[7]:


from folium import plugins
coord=[]
for lat,lng in zip(circuits['lat'],circuits['lng']):
    coord.append([lat,lng])   
maps = folium.Map(location=[45.3656,9.1651],zoom_start=5,max_bounds=True,no_wrap=True,tiles='cartodbpositron') 
folium.plugins.Fullscreen().add_to(maps)
for i,j in zip(coord,circuits.name):
    marker = folium.Marker(
        location=i,
        icon=folium.Icon(icon="star",color='red'),
        popup="<strong>{0}</strong>".format(j))  
    marker.add_to(maps)
maps


# ## 2.2 All time F1 records (drivers)

# In[8]:


head = 10
#Driver wins
dfDriverWins = dfRaceResults[(dfRaceResults['position']== '1')]
dfDriverWins['position_rank'] = dfDriverWins['position'].astype(int)
dfDriverWins = dfDriverWins.groupby(['full_name','nationality_x'])['position_rank'].sum().reset_index()
dfDriverWins = dfDriverWins.sort_values(by=['position_rank'], ascending=False).head(head)
#Driver poles
dfDriverPoles = dfRaceResults[dfRaceResults['grid']== 1].groupby(by=['full_name','nationality_x'])['grid'].sum().reset_index()
dfDriverPoles = dfDriverPoles.sort_values(by=['grid'], ascending=False).head(head)
#Driver titles
dfDriverSum = dfRaceResults.groupby(['year','full_name'])['points'].sum().reset_index()
dfDriverTiles = dfDriverSum.loc[dfDriverSum.reset_index().groupby(['year'])['points'].idxmax()]
dfDriverTiles = dfDriverTiles['full_name'].value_counts().reset_index()
dfDriverTiles.rename(columns={'index':'driver','full_name':'titles'}, inplace = True)
dfDriverTiles = dfDriverTiles.sort_values(by=['titles'], ascending=False).head(head)
#Driver podiums
dfDriverPodiums = dfRaceResults[((dfRaceResults['positionText'].isin(['1','2','3']) ))]
dfDriverPodiums['position_rank'] = dfDriverPodiums['positionText']
dfDriverPodiums = dfDriverPodiums.groupby(['full_name','nationality_x'])['position_rank'].count().reset_index()
dfDriverPodiums = dfDriverPodiums.sort_values(by=['position_rank'], ascending=False).head(head)
#Driver points (not adjusted to current points system(since 2010))
dfDriverPoints = dfRaceResults.groupby(['full_name','nationality_x'])['points'].sum().reset_index()
dfDriverPoints = dfDriverPoints.sort_values(by=['points'], ascending=False).head(head)
#Drivers fastest laps
dfDriverFastestLap = dfRaceResults[(dfRaceResults['rank']== '1')]
dfDriverFastestLap['lap_rank'] = dfDriverFastestLap['rank'].astype(int)
dfDriverFastestLap = dfDriverFastestLap.groupby(['full_name','nationality_x'])['lap_rank'].sum().reset_index()
dfDriverFastestLap = dfDriverFastestLap.sort_values(by=['lap_rank'], ascending=False).head(head)

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=('Drivers with most wins','Drivers with most poles','Drivers with most titles','Drivers with most podiums','Drivers with most points scored in races','Drivers with most fastest laps'),
    horizontal_spacing = 0.12,
    vertical_spacing = 0.25)

fig.add_trace(go.Bar(
                x=dfDriverWins['full_name'],
                y=dfDriverWins["position_rank"],
                hovertext=dfDriverWins['nationality_x'],
                orientation='v'),
                row=1, col=1)
fig.add_trace(go.Bar(
                x=dfDriverPoles['full_name'],
                y=dfDriverPoles['grid'],
                hovertext = dfDriverPoles['nationality_x'],
                orientation='v'),
                row=1, col=2)
fig.add_trace(go.Bar(
                x=dfDriverTiles['driver'],
                y=dfDriverTiles['titles'], 
                orientation='v'),
                row=1, col=3)
fig.add_trace(go.Bar(
                x=dfDriverPodiums['full_name'],
                y=dfDriverPodiums["position_rank"],
                hovertext=dfDriverPodiums['nationality_x'],
                orientation='v'),
                row=2, col=1)
fig.add_trace(go.Bar(
                x=dfDriverPoints['full_name'],
                y=dfDriverPoints["points"],
                hovertext=dfDriverPoints['nationality_x'],
                orientation='v'),
                row=2, col=2)
fig.add_trace(go.Bar(
                x=dfDriverFastestLap['full_name'],
                y=dfDriverFastestLap['lap_rank'],
                hovertext=dfDriverFastestLap['nationality_x'],
                orientation='v'),
                row=2, col=3)   
                                                                                                        
fig.update_layout(title_text='<b> F1 drivers all time records<b>', 
                  titlefont={'size':25},
                  title_x=0.5,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template = "plotly_dark"
                 )

fig.show()





# Notes:
# - Points system have changed in 2010 ,due to this fact, chart ' Drivers with most points' heavily favours these ones who were driving in 2010s/2020s.
# - Fastest laps are counted since 2004 due to lack of data before. Technically it is possible to get these data by merging 'lap_times.csv' with dataset ,however due to its size  idea was dropped.

# ## 2.3 All time F1 records (constructors)

# In[9]:


head = 10
#Constructor wins
dfConstructorWins = dfRaceResults[(dfRaceResults['position']== '1')]
dfConstructorWins['position_rank'] = dfConstructorWins['position'].astype(int)
dfConstructorWins = dfConstructorWins.groupby(['constructorRef'])['position_rank'].sum().reset_index()
dfConstructorWins = dfConstructorWins.sort_values(by=['position_rank'], ascending=False).head(head)
#Constructor poles
dfConstructorPoles = dfRaceResults[dfRaceResults['grid']== 1].groupby(by=['constructorRef'])['grid'].sum().reset_index()
dfConstructorPoles = dfConstructorPoles.sort_values(by=['grid'], ascending=False).head(head)
#Constructor titles(since 1958)
dfFilteredResults=dfRaceResults[(dfRaceResults['year'] > 1958) & (dfRaceResults['year'] < 2022)]
dfConstructorSum = dfFilteredResults.groupby(['year','constructorRef'])['points'].sum().reset_index()
dfConstructorTiles = dfConstructorSum.loc[dfConstructorSum.reset_index().groupby(['year'])['points'].idxmax()]
dfConstructorTiles = dfConstructorTiles['constructorRef'].value_counts().reset_index()
dfConstructorTiles.rename(columns={'index':'constructor','constructorRef':'titles'}, inplace = True)
dfConstructorTiles = dfConstructorTiles.sort_values(by=['titles'], ascending=False).head(head)
#Constructor podiums finishes
dfConstructorPodiums = dfRaceResults[((dfRaceResults['positionText'].isin(['1','2','3']) ))]
dfConstructorPodiums['position_rank'] = dfConstructorPodiums['positionText']
dfConstructorPodiums = dfConstructorPodiums.groupby(['constructorRef'])['position_rank'].count().reset_index()
dfConstructorPodiums = dfConstructorPodiums.sort_values(by=['position_rank'], ascending=False).head(head)
#Constructor points (not adjusted to current points system(since 2010))
dfConstructorPoints = dfRaceResults.groupby(['constructorRef'])['points'].sum().reset_index()
dfConstructorPoints = dfConstructorPoints.sort_values(by=['points'], ascending=False).head(head)
#Constructor fastest laps
dfConstructorFastestLap = dfRaceResults[(dfRaceResults['rank']== '1')]
dfConstructorFastestLap['lap_rank'] = dfConstructorFastestLap['rank'].astype(int)
dfConstructorFastestLap = dfConstructorFastestLap.groupby(['constructorRef'])['lap_rank'].sum().reset_index()
dfConstructorFastestLap = dfConstructorFastestLap.sort_values(by=['lap_rank'], ascending=False).head(head)

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=('Constructors with most wins','Constructors with most poles','Constructor with most constructor titles','Constructors with most podium finishes','Constructors with most points scored in races','Constructors with most fastest laps'),
    horizontal_spacing = 0.12,
    vertical_spacing = 0.25)

fig.add_trace(go.Bar(
                x=dfConstructorWins['constructorRef'],
                y=dfConstructorWins["position_rank"],
                orientation='v'),
                row=1, col=1)
fig.add_trace(go.Bar(
                x=dfConstructorPoles['constructorRef'],
                y=dfConstructorPoles['grid'],
                orientation='v'),
                row=1, col=2)
fig.add_trace(go.Bar(
                x=dfConstructorTiles['constructor'],
                y=dfConstructorTiles['titles'], 
                orientation='v'),
                row=1, col=3)
fig.add_trace(go.Bar(
                x=dfConstructorPodiums['constructorRef'],
                y=dfConstructorPodiums["position_rank"],
                orientation='v'),
                row=2, col=1)
fig.add_trace(go.Bar(
                x=dfConstructorPoints['constructorRef'],
                y=dfConstructorPoints["points"],
                orientation='v'),
                row=2, col=2)
fig.add_trace(go.Bar(
                x=dfConstructorFastestLap['constructorRef'],
                y=dfConstructorFastestLap['lap_rank'],
                orientation='v'),
                row=2, col=3)   
                                                                                                        
fig.update_layout(title_text='<b> F1 constructor all time records<b>', 
                  titlefont={'size':25},
                  title_x=0.5,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template = "plotly_dark",
                 )

fig.show()


# Notes:
# - Constructor championship title is being rewarded since 1958.
# - Data grouped by constructor reference to avoid potential problems with merging same teams into one( due to different names at certain time periods). 

# ## 2.4 F1 drivers season records

# In[10]:


#Driver wins most per season
dfRaceResults[dfRaceResults.position== 1].groupby(['year', 'full_name']).resultId.count().groupby('year')
dfDriverWins = dfRaceResults[(dfRaceResults['position']== '1')]
dfDriverWins['wins_per_season'] = dfDriverWins['position'].astype(int)
dfDriverWins = dfDriverWins.groupby(['full_name','year'])['wins_per_season'].count().reset_index()
dfDriverWins = dfDriverWins.sort_values(['year','wins_per_season'],ascending=[True,False]).drop_duplicates(['year'])

#Driver poles most per season
dfDriverPoles = dfRaceResults[dfRaceResults['grid']== 1].groupby(by=['full_name','year'])['grid'].sum().reset_index()
dfDriverPoles = dfDriverPoles.sort_values(['year','grid'],ascending=[True,False]).drop_duplicates(['year'])

#Driver most podiums per season
dfDriverPodiums = dfRaceResults[((dfRaceResults['positionText'].isin(['1','2','3']) ))]
dfDriverPodiums['podiums_per_season'] = dfDriverPodiums['positionText']
dfDriverPodiums = dfDriverPodiums.groupby(['full_name','year'])['podiums_per_season'].count().reset_index()
dfDriverPodiums = dfDriverPodiums.sort_values(['year','podiums_per_season'],ascending=[True,False]).drop_duplicates(['year'])

fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=('Most wins per season','Most poles per season','Most podiums per season'),
    horizontal_spacing = 0.5,
    vertical_spacing = 0.12)


fig.add_trace(go.Bar(
                x=dfDriverWins['year'],
                y=dfDriverWins["wins_per_season"],
                hovertext=dfDriverWins['full_name'],
                orientation='v'),
                row=1, col=1)
fig.add_trace(go.Bar(
                x=dfDriverPoles['year'],
                y=dfDriverPoles["grid"],
                hovertext=dfDriverPoles['full_name'],
                orientation='v'),
                row=2, col=1)
fig.add_trace(go.Bar(
                x=dfDriverPodiums['year'],
                y=dfDriverPodiums["podiums_per_season"],
                hovertext=dfDriverPodiums['full_name'],
                orientation='v'),
                row=3, col=1)
                                                                                                        
fig.update_layout(title_text='<b> F1 most of the every season record<b>', 
                  titlefont={'size':25},
                  title_x=0.5,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template = "plotly_white"
                 )

fig.show()


# # 3. Season leaderboards

# ## 3.1 Driver leaderboards

# In[11]:


traces = []
buttons = []
updatemenus = [{'active':0, "buttons":buttons}]

driver_leaderboard = dfRaceResults.groupby(['year','full_name']).agg({'points':'sum'}).reset_index()
driver_leaderboard = driver_leaderboard.sort_values(['year','points'],ascending=[True,False])

years = sorted(driver_leaderboard.year.unique())
for i, year in enumerate(years):
    visible = [False] * len(years)
    visible[i] = True
    df = driver_leaderboard[driver_leaderboard.year == year]
    colors = ['red',] * len(df.full_name.unique())
    colors[0] = 'gold'
    colors[1] = 'silver'
    colors[2] = '#cd7f32'
    traces.append(
        px.bar(data_frame=df,x='full_name', y='points').update_traces(visible=True if i==0 else False,marker_color=colors).data[0]
    )
    buttons.append(dict(label=str(year),
                        method="update",
                        args=[{"visible":visible},
                              {"title":f"Driver leaderboard season {year}"}]))


fig = go.Figure(data=traces,
                 layout=dict(updatemenus=updatemenus))
fig.update_layout(title='Driver leaderboard season 1950',title_x=0.5,template='ggplot2')
fig.show()


# Notes:
# - Sprint races point not included for 2021 and 2022

# ## 3.2 Constructor leaderboards since 1958

# In[12]:


traces = []
buttons = []
updatemenus = [{'active':0, "buttons":buttons}]

dfFilteredResults=dfRaceResults[(dfRaceResults['year'] > 1958)]
constructor_leaderboard = dfFilteredResults.groupby(['year','constructorRef']).agg({'points':'sum'}).reset_index()
constructor_leaderboard = constructor_leaderboard.sort_values(['year','points'],ascending=[True,False])

years = sorted(constructor_leaderboard.year.unique())
for i, year in enumerate(years):
    visible = [False] * len(years)
    visible[i] = True
    df = constructor_leaderboard[constructor_leaderboard.year == year]
    colors = ['red'] * len(df.constructorRef.unique())
    colors[0] = 'gold'
    colors[1] = 'silver'
    colors[2] = '#cd7f32'
    
    traces.append(
        px.bar(data_frame=df,x='constructorRef', y='points').update_traces(visible=True if i==0 else False,marker_color=colors).data[0]
    )
    buttons.append(dict(label=str(year),
                        method="update",
                        args=[{"visible":visible},
                              {"title":f"Constructor leaderboard season {year}"}]))


fig = go.Figure(data=traces,
                 layout=dict(updatemenus=updatemenus))
fig.update_layout(title='Constructor leaderboard season 1958',title_x=0.5,template='ggplot2')
fig.show()


# # 4. Championships battles

# ## 4.1 Driver championship battles (1950-2022)

# In[13]:


def championship_battle(year):
    season = dfRaceResults[dfRaceResults.year==year]
    championship_points = pd.DataFrame(season.groupby(['raceId', 'full_name'])['points'].sum().groupby('full_name').cumsum())
    championship_points = championship_points.reset_index()
    return championship_points.sort_values(['raceId','points'],ascending=[True,True])


# In[14]:


dropdown = widgets.Dropdown(options=sorted(dfRaceResults.year.unique()),value=2021,description='Season')
display(dropdown)


# In[15]:


df = championship_battle(dropdown.value)
fig = px.bar(df, y="full_name", x="points",animation_frame="raceId", range_x=[0,500])
fig.update_layout(title_text = ('<b> F1 driver championship battle of <b>'+ str(dropdown.value)), 
                  titlefont={'size':15},
                  title_x=0.5,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template='plotly_dark',
                 )
fig.show()


# ## 4.2 Constructors championship battles (1950-2022)

# In[16]:


def con_championship_battle(year):
    dfFilteredResults=dfRaceResults[(dfRaceResults['year'] > 1958)]
    season = dfFilteredResults[dfFilteredResults.year==year]
    championship_points = pd.DataFrame(season.groupby(['raceId', 'constructorRef'])['points'].sum().groupby('constructorRef').cumsum())
    championship_points = championship_points.reset_index()
    return championship_points.sort_values(['raceId','points'],ascending=[True,True])


# In[17]:


dropdown = widgets.Dropdown(options=sorted(dfFilteredResults.year.unique()),value=2021,description='Season')
display(dropdown)


# In[18]:


df = con_championship_battle(dropdown.value)
fig = px.bar(df, y="constructorRef", x="points",animation_frame="raceId", range_x=[0,800])
fig.update_layout(title_text = ('<b> F1 constructor championship battle of <b>'+ str(dropdown.value)), 
                  titlefont={'size':15},
                  title_x=0.5,
                  showlegend=False,
                  autosize=True,
                  height=1000,
                  template='plotly_dark',
                 )
fig.show()

