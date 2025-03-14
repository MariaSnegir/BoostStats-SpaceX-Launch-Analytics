# Import required libraries
import pandas as pd
import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
]
# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    dcc.Dropdown(id='site-dropdown',
                 options=dropdown_options,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),

    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},  
        value=[min_payload, max_payload]  
    ),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    color_map = ['#8A2BE2', '#4169E1']  # Purple and Blue shades

    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='🚀 Total Success Launches By Site 🌌',
            color_discrete_sequence=color_map
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts = success_counts.sort_values(by='class', ascending=True)
        
        class_labels = {0: '🚀 Unsuccessful', 1: '🌟 Successful'}
        success_counts['class'] = success_counts['class'].map(class_labels)

        fig = px.pie(
            success_counts,
            values='count',
            names='class',
            title=f'🚀 Success vs. Failed Launches for {entered_site} 🛰',
            color='class',
            color_discrete_map={'🚀 Unsuccessful': '#9370DB', '🌟 Successful': '#4682B4'},
            category_orders={'class': ['🚀 Unsuccessful', '🌟 Successful']}
        )

    fig.update_layout(
        template="plotly_dark",
        font=dict(family="Orbitron, sans-serif", size=18, color="white"),
        title_font=dict(size=26, color="#B0C4DE"),
        legend_title=dict(font=dict(size=20, color="lightgray")),
        paper_bgcolor="#1E2A47",
        plot_bgcolor="rgba(50, 60, 90, 0.9)",

        legend=dict(
            x=0.70,
            y=0.7,
            xanchor="left",
            yanchor="middle",
            font=dict(size=20),
            bgcolor="rgba(0, 0, 0, 0.3)",
            bordercolor="white",
            borderwidth=1
        )
    )

    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def scatter_chart(entered_site, payload_range):
    # Фильтрация данных по полезной нагрузке
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if entered_site == "ALL":
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color="Booster Version Category",
            title='🚀 Correlation between Payload and Success for all Sites 🌍',
            template="plotly_white",
            size_max=10,  # Размер точек
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color="Booster Version Category",
            title=f'🚀 Payload vs. Success for {entered_site} 🛰️',
            template="plotly_white",
            size_max=10,  # Размер точек
        )
    
    # Улучшаем вид графика
    fig.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Mission Success (0 - Failed, 1 - Success)",
        legend=dict(
            x=1.02,  # Чуть правее
            y=1,  
            xanchor="left",  
            yanchor="top",
            bgcolor="rgba(255, 255, 255, 0.7)",  
            bordercolor="black",
            borderwidth=1
        ),
        margin=dict(l=50, r=250, t=50, b=50)  # Отступы, чтобы легенда не налезала
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

