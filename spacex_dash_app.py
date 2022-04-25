# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Generate list of distinct launch sites
launch_site_list = list(spacex_df['Launch Site'].unique())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site_dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'All'},
                                    {'label': launch_site_list[0], 'value': launch_site_list[0]},
                                    {'label': launch_site_list[1], 'value': launch_site_list[1]},
                                    {'label': launch_site_list[2], 'value': launch_site_list[2]},
                                    {'label': launch_site_list[3], 'value': launch_site_list[3]},
                                ],
                                value='All',
                                placeholder="Select a Launch Site",
                                searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                           2500: '2500',
                                           5000:'5000',
                                           7500:'7500',
                                           10000:'10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
               Input(component_id='site_dropdown',component_property='value'))
def create_outcome_graph(launch_site_value):
    # Select data based on the launch_site_value
    if launch_site_value == 'All':
        selected_df = spacex_df.groupby('Launch Site',as_index=False).sum()
        fig = px.pie(selected_df, values='class', names='Launch Site',
             title=f'Total Booster Landing Success for {launch_site_value} Sites')
    else:
        selected_df = pd.DataFrame(spacex_df[spacex_df['Launch Site']==launch_site_value]['class'].value_counts()).reset_index()
        selected_df.rename(columns={"index": "outcome", "class": "outcome_total"}, inplace=True)
        # Let's create a more meaningful outcome category to hold values "Success" or "Failure"
        selected_df["outcome_cat"] = selected_df["outcome"].astype("category")
        # 0 will map to first item in list, "Failure"
        # 1 will map to second item in list, "Success"
        selected_df["outcome_cat"].cat.categories= ["Failure", "Success"]
        fig = px.pie(selected_df, values='outcome_total', names='outcome_cat',
             title=f'Total Booster Landing Outcome for {launch_site_value}',
             color='outcome_cat',
             color_discrete_map={'Success':'green',
                                 'Failure':'red',})

    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart',component_property='figure'),
               Input(component_id='site_dropdown',component_property='value'),
               Input(component_id='payload-slider',component_property='value'))
def create_payload_graph(launch_site_value, payload_range):
    # Select data based on the launch_site_value
    if launch_site_value == 'All':
        selected_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)']<=payload_range[1])]

        fig = px.scatter(selected_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
             title=f'Correlation between Payload and Success for {launch_site_value} Sites')
    else:
        selected_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)']<=payload_range[1]) \
            & (spacex_df['Launch Site']==launch_site_value)]

        fig = px.scatter(selected_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
             title=f'Correlation between Payload and Success for specific launch site {launch_site_value}')


    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
