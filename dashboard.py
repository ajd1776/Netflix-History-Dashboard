import dash
from dash import dcc
from dash import html
from dash import dash_table as dt
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd
from pathlib import Path
import os


# Palette
red1  = "#ff0000"
red2  = "#cc0000"
red3  = "#990000"
grey1 = "#404040"
grey2 = "#262626"
grey3 = "#0c0c0c"

# Create custom plotly template for graph objects
pio.templates["dark_red_theme"] = go.layout.Template(
    # LAYOUT
    layout = ({
    "font": {"family": "Arial, Helvetica, sans-serif",
             "color": "white"},
    "colorway": [red2, red3], # Colour of bars
    "paper_bgcolor": grey2, # Outer colour of graph
    "plot_bgcolor": grey2, # Inner colour of graph
    # Axis & grid styling
    "yaxis": {
            "gridcolor": grey2,
            "linecolor": grey3,
            "zerolinecolor": grey2}
}))




# DATA FILE PROCESSING

# Find directory for users download folder
path_to_download_folder = str(os.path.join(Path.home(), "Downloads", "NetflixViewingHistory.csv"))
main_dataframe = pd.read_csv(path_to_download_folder) # Import data from file uploaded
df = main_dataframe.copy() # Copy so original is not altered
#df = [1,2]

# Convert dates to datetime type
df["Date"] = pd.to_datetime(df["Date"])

# Extract data from "Date" column into new columns
df["Date"]         = df["Date"].dt.normalize()
df["Year"]         = df["Date"].dt.year
df["Month_number"] = df["Date"].dt.month
df["Month"]        = df["Date"].dt.month_name()
df["Day"]          = df["Date"].dt.day
df["Day_of_week"]  = df["Date"].dt.day_name()

# Split the title data into new columns
title_details = df.Title.str.split(":", expand=True, n=2)
# Use title data for new column names
df["Show_name"] = title_details[0]
df["Season"] = title_details[1]
df["Episode_name"] = title_details[2]   
# Determine whether a record is a show or a movie
df["Show_type"] = df.apply(lambda x: "Movie" if pd.isnull(x["Season"]) else "TV Show", axis=1)

# Get the year range from dataset to use in graphs and sliders
years = df["Year"].value_counts().index.sort_values()
firstYear = years[0]
lastYear = years[-1]
# Months to display
months = ["Jan", "Feb", "Mar", "Apr",
          "May", "Jun", "Jul", "Aug", 
          "Sep", "Oct", "Nov", "Dec"]

# Reformat dates to only display Year/Month/Day
# Fixes issue where timestamp was displayed as 00:00:00
df["Date"] = df["Date"].dt.strftime(f"%Y-%m-%d")

# Build dataframes for watch history data 
watch_data = df[["Date", "Show_name"]].sort_values(by=["Date"], ascending=False)
# df Shows
df_recent_show = watch_data.loc[df["Show_type"] == "TV Show"]
# df Movies
df_recent_movie = watch_data.loc[df["Show_type"] == "Movie"]

# Metrics
top_show    = df_recent_show["Show_name"].value_counts().head(1).index
ntop_show   = df_recent_show["Show_name"].value_counts().head(1)

top_movie  = df_recent_movie["Show_name"].value_counts().head(1).index
ntop_movie = df_recent_movie["Show_name"].value_counts().head(1)

most_active_day         = df["Day"].value_counts().head(1).index
nmost_active_day        = df["Day"].value_counts().head(1).to_list()

most_active_dayofweek   = df["Day_of_week"].value_counts().head(1).index
nmost_active_dayofweek  = df["Day_of_week"].value_counts().head(1).to_list()

most_active_month       = df["Month"].value_counts().head(1).index
nmost_active_month      = df["Month"].value_counts().head(1).to_list()

most_active_year        = df["Year"].value_counts().head(1).index
nmost_active_year       = df["Year"].value_counts().head(1).to_list()


# Initialises layout for main flask app to display
def init_dashboard(server):

    # INIT DASHAPP
    dash_app = dash.Dash(server=server,
                         title="Your Dashboard",
                         update_title=None,
                         routes_pathname_prefix="/dashapp/",
                         external_stylesheets=[dbc.themes.BOOTSTRAP])
    server = dash_app.server
        
    # APP LAYOUT
    dash_app.layout = dbc.Container([
        
        
        # Info Banner
        html.Div([
            html.Div([
                html.Div("This app is a beta version, errors may occur", className="banner_item"),
                html.Div("This app is a beta version, errors may occur", className="banner_item")
            ], className="banner_move")
        ], className="banner_wrap"),
    

        # Row
        dbc.Row([
            dbc.Col([
                html.H5("Recently watched shows", 
                        style={"textAlign": "center",
                            "marginTop": "10px"}),
                dt.DataTable(
                    id="recently_watched_show",
                    columns=[{"id": "Date", "name": "Date"},
                            {"id": "Show_name", "name": "Show"}],
                    data=df_recent_show.to_dict("records"),
                    page_size=5,
                    is_focused=False,

                    style_header={
                        "backgroundColor": grey2,
                        "textAlign": "center",
                        "borderTop": "0px",
                    },
                    style_data={
                        "textAlign": "center",
                        "backgroundColor": grey2,
                    },
                    style_cell={
                        "borderBottom": "0px",                    
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "Date"},
                        "width": "100px"},
                        {"if": {"column_id": "Show_name"},
                        "width": "500px",
                        "textAlign": "center"},
                    ],
                    style_as_list_view=True
                )
            ], width={"size":3}, class_name="recently_watched_show_col"),
            

            
            dbc.Col([
                html.Div([
                    html.H3("Welcome to your dashboard", id="title"),
                    html.A( "Home Page", id="btn_home", href="/", style={"textDecoration":"none", "color": "white"}),
                    html.Div([
                        html.P([html.B("Top show"), ": {}".format(ntop_show[0]), html.Br(), "{}".format(top_show[0])]), 
                        html.P([html.B("Top movie"), ": {}".format(ntop_movie[0]),html.Br(), "{}".format(top_movie[0])]),
                        html.P([html.B("Most active day"), ": {}".format(nmost_active_day[0]), html.Br(), "{}".format(most_active_day[0])]), 
                        html.P([html.B("Most active day of week"), ": {}".format(nmost_active_dayofweek[0]), html.Br(), "{}".format(most_active_dayofweek[0])]), 
                        html.P([html.B("Most active month"), ": {}".format(nmost_active_month[0]), html.Br(), "{}".format(most_active_month[0])]),
                        html.P([html.B("Most active year"), ": {}".format(nmost_active_year[0]), html.Br(), "{}".format(most_active_year[0])]),
                    ], id="metrics"),
                ], id="metrics_container"),
                
            ], width={"size":6}, class_name="welcome"),
            
            
            
            dbc.Col([
                html.H5("Recently watched movies", 
                        style={"textAlign": "center",
                            "marginTop": "10px"}),
                dt.DataTable(
                    id="recently_watched_movie",
                    columns=[{"id": "Date", "name": "Date"},
                            {"id": "Show_name", "name": "Movie"}],
                    data=df_recent_movie.to_dict("records"),
                    page_size=5,
                    is_focused=False,
                    
                    style_header={
                        "backgroundColor": grey2,
                        "textAlign": "center",
                        "borderTop": "0px",
                    },
                    style_data={
                        "textAlign": "center",
                        "backgroundColor": grey2,
                    },
                    style_cell={
                        "borderBottom": "0px",                    
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "Date"},
                        "width": "100px"},
                        {"if": {"column_id": "Show_name"},
                        "width": "500px",
                        "textAlign": "center"},
                    ],
                    style_as_list_view=True
                )
            ], width={"size":3}, class_name="recently_watched_movie_col")
        ], justify="center"),
        
        
        
        # Row
        dbc.Row([
            # Barchart 1 and range slider
            dbc.Col([
                dcc.Graph(id="barchart1", figure={}),
                dcc.RangeSlider(
                    id="range_slider1",
                    min=firstYear,
                    max=lastYear,
                    step=1,
                    value=[firstYear, lastYear],
                    marks={year : "{}".format(year) for year in (years)},
                ),
            ], width={"size":5}, class_name="chart1"),
            
            # Barchart 2 & 2 slide & btn
            dbc.Col([
                dcc.Graph(id="barchart2", figure={}),
                dcc.Slider(
                    id="slider2",
                    min=firstYear,
                    max=lastYear,
                    step=1,
                    value=lastYear,
                    marks={year : "{}".format(year) for year in (years)},
                ),
                html.Br(),
                html.Div([
                    dcc.Slider(
                        id="slider1",
                        min=1,
                        max=25,
                        step=1,
                        value=5,
                    ),
                    html.Button(
                        children="Type",
                        id="btn1",
                        n_clicks=0
                    ),
                ], className="bc2_container"),
            ], width={"size":6}, class_name="chart2"),
        ], justify="center"),
        
        
        
        # Row
        dbc.Row([
            # Barchart 3 and range slider
            dbc.Col([
                dcc.Graph(id="barchart3", figure={}),             
                dcc.RangeSlider(
                    id="range_slider3",
                    min=firstYear,
                    max=lastYear,
                    step=1,
                    value=[firstYear, lastYear],
                    marks={year : "{}".format(year) for year in (years)},
                ),
                html.Br(),
                dcc.RangeSlider(
                    id="range_slider4",
                    min=1,
                    max=12,
                    step=1,
                    value=[1, 12],
                    marks={n : "{}".format(months[n-1]) for n in range(1, 13)},
                ),
                html.Br(),
            ], width={"size":8}, class_name="chart3"),
            
            # Pie chart 1 and slider
            dbc.Col([
                dcc.Graph(id="piechart1", figure={}),
                dcc.Slider(
                    id="slider3",
                    min=0,
                    max=0.95,
                    step=0.05,
                    value=0.5,
                ),
                
            ], width={"size":4}, class_name="chart4"),
        ], justify="center"),
        
        
        
        # History table
        dbc.Row([            
            dbc.Col([
                #html.H3("Your entire history", id="hist_title"),
                dt.DataTable(
                    id="history_table",
                    #"Title", "Date", "Year", "Month", "Day", "Day_of_week",
                    #"Show_name", "Season", "Episode_name", "Show_type",
                    #dtype="object")
                    columns=[{"id": "Date", "name": "Date"},
                            {"id": "Month", "name": "Month"},
                            {"id": "Day_of_week", "name": "Day of week"},
                            {"id": "Title", "name": "Title"},
                            ],
                    data=df.to_dict("records"),
                    page_size=20,
                    
                    style_header={
                        "backgroundColor": grey2,
                        "textAlign": "center",
                        "borderTop": "0px",
                    },
                    style_data={
                        "textAlign": "center",
                        "backgroundColor": grey2,
                        "whitespace": "normal",
                        "height": "auto",
                    },
                    style_cell={
                        "borderBottom": "0px"
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "Date"},
                        "width": "100px"},
                        {"if": {"column_id": "Month"},
                        "width": "100px",
                        "textAlign": "center"},
                        {"if": {"column_id": "Day_of_week"},
                        "width": "100px",
                        "textAlign": "center"},
                        {"if": {"column_id": "Title"},
                        "width": "600px",
                        "textAlign": "center"},
                    ],
                    
                    style_as_list_view=True
                ),
                
                html.Button("Download Expanded History", id="btn_download"),
                dcc.Download(id="download_hist"),
                
            ], width={"size":11}, class_name="history_col"),
        ], justify="center"),
        
        html.Br(),
    ], fluid=True)
    
    init_callbacks(dash_app)
    
    return dash_app.server


# Initialises callbacks for main flask app
def init_callbacks(dash_app):
    
    
    # CALLBACK FOR DOWNLOAD BUTTON
    @dash_app.callback(
        Output("download_hist", "data"),
        Input("btn_download", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_hist(n_clicks):
        return dcc.send_data_frame(df.to_csv, "ExpandedNetflixHistory.csv")
        
    # CALLBACK FOR BARCHART 1
    @dash_app.callback(
        Output("barchart1", "figure"),
        Input("range_slider1", "value")
    )
    def update_barchart1(value):
        #print(value[0], value[1])
        
        # Create new dataframe based on the given range from the slider
        dft = df[((df["Year"] >= value[0]) & (df["Year"] <= value[1]))]
        
        # Title name
        if value[0] == value[1]:
            titleCustom = "Monthly activity in {}".format(value[0])
        else:
            titleCustom = "Monthly activity from {} - {}".format(value[0], value[1])

        # Only plots if there is data to plot   
        if (not dft.empty):
            # Return graph with data
            fig = px.bar(dft, 
                        x=dft["Month"].value_counts().index,
                        y=dft["Month"].value_counts(),
                        labels=dict(x="", y=""),
                        text_auto=True,
                        title=titleCustom,
                        template="dark_red_theme")
            fig.update_traces(textangle=0, textposition="outside")
            return fig
        else:
            # Return empty chart
            fig = px.bar(x = [0], y = [0],
                        title="No data to display",
                        template="dark_red_theme")
            return fig



    # CALLBACK FOR BARCHART 2
    @dash_app.callback(
        Output("barchart2", "figure"),
        [Input("slider1", "value"),
        Input("slider2", "value"),
        Input("btn1", "n_clicks")]
    )
    def update_barchart2(slider1, slider2, n_clicks):
        
        # Switch between shows and movies
        if n_clicks % 2 == 0:
            filter_name = "TV Show"
        else:
            filter_name = "Movie"

        # Create new dataframe based on the given range from the slider
        dft = df[(df["Year"] == slider2) & (df["Show_type"] == filter_name)]
        #df2["Show_name"].value_counts().head(10)

        # Title name
        if slider1 == 1:
            if filter_name == "TV Show":
                titleCustom = "Top show of {}".format(slider2)
            else:
                titleCustom = "Top movie of {}".format(slider2)
        else:
            if filter_name == "TV Show":
                titleCustom = "Top {} shows in {}".format(slider1, slider2)
            else:
                titleCustom = "Top {} movies in {}".format(slider1, slider2)

        # Only plots if there is data to plot   
        if (not dft.empty):
            # Return graph with data
            fig = px.bar(dft, 
                        x=dft["Show_name"].value_counts().head(slider1).index,
                        y=dft["Show_name"].value_counts().head(slider1),
                        text_auto=True,
                        title=str(titleCustom),
                        template="dark_red_theme",
                        labels=dict(x="", y=""))
            fig.update_traces(textangle=0, textposition="outside")
            return fig
        else:
            # Return empty chart
            fig = px.bar(x = [0], y = [0],
                        title="No data to display",
                        template="dark_red_theme")
            return fig



    # CALLBACK FOR BARCHART 3
    @dash_app.callback(
        Output("barchart3", "figure"),
        [Input("range_slider3", "value"),
        Input("range_slider4", "value"),
        ]
    )
    def update_barchart3(value, range_slider4):
        
        # Create new dataframe based on the given ranges from the sliders
        # Year range chosen and the month range within that year range
        dft = df[ ((df["Year"] >= value[0])  & 
                (df["Year"] <= value[1])) &
                ((df["Month_number"] >= range_slider4[0]) & 
                (df["Month_number"] <= range_slider4[1])) ]

            
        # Title name
        if value[0] == value[1]:
            titleCustom = "Daily activity in {}".format(value[0])
        else: 
            titleCustom = "Daily activity from {} - {}".format(value[0], value[1])
            
        # Only plots if there is data to plot   
        if (not dft.empty):
            # Return graph with data
            fig = px.bar(dft, 
                        x = dft["Day"].value_counts().index,
                        y = dft["Day"].value_counts(),
                        text_auto=True,
                        title=titleCustom,
                        template="dark_red_theme",
                        labels=dict(x="", y=""))
            fig.update_traces(textangle=0, textposition="outside")
            fig.update_xaxes(dtick=1)
            return fig
        else:
            # Return empty chart
            fig = px.bar(x = [0], y = [0],
                        title="No data to display",
                        template="dark_red_theme")
            return fig



    # CALLBACK FOR PIECHART 1 
    @dash_app.callback(
        Output("piechart1", "figure"),
        Input("slider3", "value")
    )
    def update_pie_chart(value):
        
        values = [sum(df_recent_show["Show_name"].value_counts()),  # n Shows
                sum(df_recent_movie["Show_name"].value_counts())] # n Movies
        names = ["Shows", "Movies"] # Labels
        
        fig = px.pie(df,
                    values=values,
                    names=names,
                    template="dark_red_theme",
                    title="Shows / Movies",
                    hole=value)
        fig.layout.update(showlegend=False)
        
        return fig