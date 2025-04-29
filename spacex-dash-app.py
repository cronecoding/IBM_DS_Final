# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),

    # Add a text element to display the success and failure counts
    html.Div(id='launch-counts', style={'textAlign': 'center', 'font-size': 20}),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    [Output(component_id='success-pie-chart', component_property='figure'),
     Output(component_id='launch-counts', component_property='children')],
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Get success and failure counts
    success_count = (filtered_df['class'] == 1).sum()
    failure_count = (filtered_df['class'] == 0).sum()
    
    # Create a message with counts
    launch_counts = f"Successes: {success_count} | Failures: {failure_count}"
    
    # Define fixed colors
    color_map = {0: 'red', 1: 'green'}  # Red for Failure, Green for Success
    
    # Create the pie chart with fixed colors
    fig = px.pie(filtered_df, 
                 names='class', 
                 title=f'Launch Success for {entered_site if entered_site != "ALL" else "All Sites"}',
                 labels={'class': 'Launch Outcome'},
                 color='class',  # Set the color based on the 'class' column
                 color_discrete_map=color_map)  # Use the fixed color map
    
    return fig, launch_counts

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(entered_site, payload_range):
    filtered_df = spacex_df
    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] >= payload_range[0]]
    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] <= payload_range[1]]

    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    filtered_df['class'] = filtered_df['class'].astype(str)

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                     color='Booster Version Category', 
                     title=f'Payload vs Launch Success for {entered_site if entered_site != "ALL" else "All Sites"}',
                     labels={'class': 'Launch Success (0=Failure, 1=Success)'}, 
                     category_orders={'class': ['0', '1']})
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
