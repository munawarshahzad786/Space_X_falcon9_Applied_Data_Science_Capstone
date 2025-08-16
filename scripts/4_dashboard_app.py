"""
Falcon 9 Project - 4-dashboard_app.py
Author: Muhammad Munawar Shahzad
Date: 2025-08-15
"""
import requests
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fetch data from SpaceX API
def fetch_launch_data():
    try:
        # Get all launches
        launches_url = "https://api.spacexdata.com/v4/launches"
        launches_response = requests.get(launches_url)
        launches_response.raise_for_status()
        all_launches = launches_response.json()
        
        print(f"Total launches received: {len(all_launches)}")
        
        # Get all rockets to map IDs to names
        rockets_url = "https://api.spacexdata.com/v4/rockets"
        rockets_response = requests.get(rockets_url)
        rockets_response.raise_for_status()
        all_rockets = rockets_response.json()
        
        # Create a mapping of rocket ID to rocket name
        rocket_map = {rocket['id']: rocket['name'] for rocket in all_rockets}
        print(f"Rocket types available: {list(rocket_map.values())}")
        
        # Get all payloads to map IDs to payload details
        payloads_url = "https://api.spacexdata.com/v4/payloads"
        payloads_response = requests.get(payloads_url)
        payloads_response.raise_for_status()
        all_payloads = payloads_response.json()
        
        # Create a mapping of payload ID to payload details
        payload_map = {payload['id']: payload for payload in all_payloads}
        print(f"Payloads available: {len(payload_map)}")
        
        # Get all launchpads to map IDs to launchpad details
        launchpads_url = "https://api.spacexdata.com/v4/launchpads"
        launchpads_response = requests.get(launchpads_url)
        launchpads_response.raise_for_status()
        all_launchpads = launchpads_response.json()
        
        # Create a mapping of launchpad ID to launchpad details
        launchpad_map = {launchpad['id']: launchpad for launchpad in all_launchpads}
        print(f"Launchpads available: {len(launchpad_map)}")
        
        # Filter for Falcon 9 launches
        falcon9_launches = [
            launch for launch in all_launches 
            if isinstance(launch, dict) and launch.get('rocket') and rocket_map.get(launch['rocket']) == 'Falcon 9'
        ]
        
        print(f"Falcon 9 launches found: {len(falcon9_launches)}")
        
        # Sort by flight number (descending) and limit to 1000
        falcon9_launches.sort(key=lambda x: x.get('flight_number', 0), reverse=True)
        
        # Store the mappings globally for use in data processing
        global PAYLOAD_MAP, LAUNCHPAD_MAP
        PAYLOAD_MAP = payload_map
        LAUNCHPAD_MAP = launchpad_map
        
        return falcon9_launches[:1000]
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Process launch data
def process_launch_data(launches):
    if not launches:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.json_normalize(launches)
    
    # Clean and process data
    df['date_utc'] = pd.to_datetime(df['date_utc'])
    
    # Debug: Check payload structure
    if len(df) > 0:
        sample_payload = df['payloads'].iloc[0]
        print(f"Sample payload structure: {sample_payload}")
        if sample_payload and len(sample_payload) > 0:
            print(f"Sample payload[0] keys: {list(sample_payload[0].keys()) if isinstance(sample_payload[0], dict) else 'Not a dict'}")
    
    # Extract payload mass using the global payload map
    def extract_payload_mass(payload_ids):
        if not payload_ids or not isinstance(payload_ids, list) or len(payload_ids) == 0:
            return None
        
        # Get the first payload ID
        payload_id = payload_ids[0]
        if payload_id in PAYLOAD_MAP:
            payload = PAYLOAD_MAP[payload_id]
            # Try different possible field names
            for field in ['mass_kg', 'mass', 'mass_lbs']:
                if field in payload and payload[field] is not None:
                    if field == 'mass_lbs':
                        return payload[field] * 0.453592  # Convert lbs to kg
                    return payload[field]
        return None
    
    df['payload_mass_kg'] = df['payloads'].apply(extract_payload_mass)
    print(f"Payload mass extraction - non-null values: {df['payload_mass_kg'].notna().sum()}")
    
    # Debug: Check launchpad structure
    if len(df) > 0:
        sample_launchpad = df['launchpad'].iloc[0]
        print(f"Sample launchpad structure: {sample_launchpad}")
        if isinstance(sample_launchpad, dict):
            print(f"Sample launchpad keys: {list(sample_launchpad.keys())}")
    
    # Extract launch site using the global launchpad map
    def extract_launch_site(launchpad_id):
        if not launchpad_id or launchpad_id not in LAUNCHPAD_MAP:
            return 'Unknown'
        
        launchpad = LAUNCHPAD_MAP[launchpad_id]
        
        # Try to get location name from different possible paths
        if 'location' in launchpad and isinstance(launchpad['location'], dict):
            if 'name' in launchpad['location']:
                return launchpad['location']['name']
            elif 'full_name' in launchpad['location']:
                return launchpad['location']['full_name']
        
        # If no location info, try to get name directly
        if 'name' in launchpad:
            return launchpad['name']
        elif 'full_name' in launchpad:
            return launchpad['full_name']
        
        return 'Unknown'
    
    df['launch_site'] = df['launchpad'].apply(extract_launch_site)
    print(f"Launch site extraction - non-null values: {df['launch_site'].notna().sum()}")
    print(f"Unique launch sites: {df['launch_site'].unique()}")
    
    # Extract launch outcome
    df['launch_outcome'] = df['success'].apply(lambda x: 'Success' if x else 'Failure')
    
    # Remove rows with missing payload mass, but be more lenient
    initial_count = len(df)
    df = df.dropna(subset=['payload_mass_kg'])
    final_count = len(df)
    print(f"Rows dropped due to missing payload mass: {initial_count - final_count}")
    
    return df

# Fetch and process data
launches = fetch_launch_data()
print(f"Processing {len(launches)} launches...")
df = process_launch_data(launches)
print(f"DataFrame shape after processing: {df.shape}")
print(f"DataFrame columns: {list(df.columns)}")

if df.empty:
    print("No data available. Please check the API connection.")
    exit()

# Calculate success counts and ratios
success_counts = df.groupby('launch_site')['launch_outcome'].value_counts().unstack().fillna(0)
success_counts['Total'] = success_counts['Success'] + success_counts['Failure']
success_counts['Success_Ratio'] = (success_counts['Success'] / success_counts['Total'] * 100).round(2)

# Find site with highest success ratio
highest_ratio_site = success_counts.loc[success_counts['Success_Ratio'].idxmax()]

# Initialize the Dash app
app = dash.Dash(__name__, title="Falcon 9 Launch Dashboard")

# Define the app layout
app.layout = html.Div([
    html.H1(" Falcon 9 Launch Dashboard", 
             style={'textAlign': 'center', 'color': '#1f77b4', 'marginBottom': '30px'}),
    
    # Summary statistics
    html.Div([
        html.Div([
            html.H4(f"Total Launches: {len(df)}"),
            html.H4(f"Success Rate: {(df['launch_outcome'].value_counts(normalize=True)['Success'] * 100):.1f}%"),
            html.H4(f"Total Sites: {len(df['launch_site'].unique())}")
        ], style={'textAlign': 'center', 'marginBottom': '20px'})
    ]),
    
    # First row: Pie charts
    html.Div([
        # Launch success count pie chart
        html.Div([
            html.H3("📊 Launch Success Count by Site", 
                     style={'textAlign': 'center', 'color': '#2ca02c'}),
            dcc.Graph(id='pie-launch-success', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        # Launch success ratio pie chart for highest ratio site
        html.Div([
            html.H3(f"🏆 {highest_ratio_site.name} - Highest Success Ratio", 
                     style={'textAlign': 'center', 'color': '#ff7f0e'}),
            dcc.Graph(id='pie-launch-ratio', style={'height': '400px'})
        ], style={'width': '50%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),
    
    # Second row: Scatter plot with controls
    html.Div([
        html.H3("📈 Payload vs Launch Outcome Analysis", 
                 style={'textAlign': 'center', 'color': '#d62728', 'marginBottom': '20px'}),
        
        # Payload range slider
        html.Div([
            html.Label("Payload Mass Range (kg):", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='payload-slider',
                min=int(df['payload_mass_kg'].min()),
                max=int(df['payload_mass_kg'].max()),
                step=100,
                value=[int(df['payload_mass_kg'].min()), int(df['payload_mass_kg'].max())],
                marks={
                    int(df['payload_mass_kg'].min()): f"{int(df['payload_mass_kg'].min()):,}",
                    int(df['payload_mass_kg'].max()): f"{int(df['payload_mass_kg'].max()):,}"
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '20px'}),
        
        # Scatter plot
        dcc.Graph(id='scatter-payload', style={'height': '500px'})
    ]),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P("Data source: SpaceX API v4", 
               style={'textAlign': 'center', 'color': '#666', 'fontSize': '12px'})
    ], style={'marginTop': '30px'})
], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})

# Callback to update the launch success count pie chart
@app.callback(
    Output('pie-launch-success', 'figure'),
    Input('payload-slider', 'value')
)
def update_pie_success(selected_range):
    if not selected_range:
        return go.Figure()
    
    low, high = selected_range
    filtered_df = df[(df['payload_mass_kg'] >= low) & (df['payload_mass_kg'] <= high)]
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data in selected range",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    success_count = filtered_df.groupby('launch_site')['launch_outcome'].value_counts().unstack().fillna(0)
    
    fig = px.pie(
        values=success_count['Success'],
        names=success_count.index,
        title=f'Launch Success Count by Site<br><sub>Payload Range: {low:,} - {high:,} kg</sub>',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title_x=0.5,
        showlegend=True,
        height=400
    )
    
    return fig

# Callback to update the launch success ratio pie chart
@app.callback(
    Output('pie-launch-ratio', 'figure'),
    Input('payload-slider', 'value')
)
def update_pie_ratio(selected_range):
    if not selected_range:
        return go.Figure()
    
    low, high = selected_range
    filtered_df = df[(df['payload_mass_kg'] >= low) & (df['payload_mass_kg'] <= high)]
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data in selected range",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Calculate success ratio for the highest ratio site in filtered data
    site_stats = filtered_df.groupby('launch_site')['launch_outcome'].value_counts().unstack().fillna(0)
    site_stats['Total'] = site_stats['Success'] + site_stats['Failure']
    site_stats['Success_Ratio'] = (site_stats['Success'] / site_stats['Total'] * 100).round(2)
    
    if site_stats.empty or site_stats['Total'].sum() == 0:
        return go.Figure().add_annotation(
            text="No data in selected range",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Get the site with highest success ratio in filtered data
    best_site = site_stats.loc[site_stats['Success_Ratio'].idxmax()]
    
    # Create title without nested quotes
    title_text = f'{best_site.name}<br>Success Ratio: {best_site["Success_Ratio"]:.1f}%<br><sub>Payload Range: {low:,} - {high:,} kg</sub>'
    
    fig = px.pie(
        values=[best_site['Success'], best_site['Failure']],
        names=['Success', 'Failure'],
        title=title_text,
        color_discrete_sequence=['#2ca02c', '#d62728']
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title_x=0.5,
        showlegend=True,
        height=400
    )
    
    return fig

# Callback to update the scatter plot
@app.callback(
    Output('scatter-payload', 'figure'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_range):
    if not selected_range:
        return go.Figure()
    
    low, high = selected_range
    filtered_df = df[(df['payload_mass_kg'] >= low) & (df['payload_mass_kg'] <= high)]
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data in selected range",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig = px.scatter(
        filtered_df,
        x='payload_mass_kg',
        y='launch_outcome',
        color='launch_site',
        size='payload_mass_kg',
        hover_data=['date_utc', 'launch_site'],
        title=f'Payload vs Launch Outcome<br><sub>Payload Range: {low:,} - {high:,} kg</sub>',
        labels={'payload_mass_kg': 'Payload Mass (kg)', 'launch_outcome': 'Launch Outcome'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Launch Outcome",
        height=500,
        showlegend=True
    )
    
    # Update x-axis to show comma-separated thousands
    fig.update_xaxes(tickformat=",")
    
    return fig

# Run the app
if __name__ == '__main__':
    print(f"Dashboard loaded with {len(df)} launches from {len(df['launch_site'].unique())} sites")
    print(f"Payload mass range: {df['payload_mass_kg'].min():,.0f} - {df['payload_mass_kg'].max():,.0f} kg")
    print("Starting dashboard server...")
    app.run(debug=True, host='127.0.0.1', port=8050)
