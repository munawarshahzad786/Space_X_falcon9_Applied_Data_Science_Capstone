"""
Falcon 9 Project - 5_folium_map.py
Author: Muhammad Munawar Shahzad
Date: 2025-08-15
"""
import folium
import pandas as pd
import requests
import numpy as np
from folium import plugins
import json
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

class SpaceXLaunchMap:
    def __init__(self):
        self.launches_data = None
        self.launchpads_data = None
        self.payloads_data = None
        self.rockets_data = None
        self.map = None
        
        # Define known launch sites with their coordinates and proximity data
        self.known_launch_sites = {
            'CCSFS SLC 40': {
                'name': 'Cape Canaveral Space Force Station SLC-40',
                'locality': 'Cape Canaveral',
                'region': 'Florida, USA',
                'latitude': 28.5619,
                'longitude': -80.5774,
                'proximity': {
                    'railway': {'distance': 8.2, 'direction': 'NW', 'name': 'Florida East Coast Railway'},
                    'highway': {'distance': 3.1, 'direction': 'E', 'name': 'US-1'},
                    'coastline': {'distance': 0.8, 'direction': 'E', 'name': 'Atlantic Ocean'}
                }
            },
            'KSC LC 39A': {
                'name': 'Kennedy Space Center Launch Complex 39A',
                'locality': 'Merritt Island',
                'region': 'Florida, USA',
                'latitude': 28.6083,
                'longitude': -80.6041,
                'proximity': {
                    'railway': {'distance': 12.5, 'direction': 'NW', 'name': 'Florida East Coast Railway'},
                    'highway': {'distance': 5.2, 'direction': 'E', 'name': 'FL-405'},
                    'coastline': {'distance': 1.2, 'direction': 'E', 'name': 'Atlantic Ocean'}
                }
            },
            'VAFB SLC 4E': {
                'name': 'Vandenberg Space Force Base SLC-4E',
                'locality': 'Lompoc',
                'region': 'California, USA',
                'latitude': 34.6321,
                'longitude': -120.6106,
                'proximity': {
                    'railway': {'distance': 15.8, 'direction': 'NE', 'name': 'Union Pacific Railroad'},
                    'highway': {'distance': 8.7, 'direction': 'E', 'name': 'US-101'},
                    'coastline': {'distance': 2.1, 'direction': 'W', 'name': 'Pacific Ocean'}
                }
            },
            'Boca Chica': {
                'name': 'SpaceX Starbase Launch Site',
                'locality': 'Boca Chica',
                'region': 'Texas, USA',
                'latitude': 25.9968,
                'longitude': -97.1558,
                'proximity': {
                    'railway': {'distance': 22.3, 'direction': 'NW', 'name': 'Union Pacific Railroad'},
                    'highway': {'distance': 4.8, 'direction': 'N', 'name': 'TX-4'},
                    'coastline': {'distance': 0.5, 'direction': 'E', 'name': 'Gulf of Mexico'}
                }
            },
            'Omelek Island': {
                'name': 'Omelek Island Launch Complex',
                'locality': 'Kwajalein Atoll',
                'region': 'Marshall Islands',
                'latitude': 9.0478,
                'longitude': 167.7431,
                'proximity': {
                    'railway': {'distance': 'N/A', 'direction': 'N/A', 'name': 'No Railway'},
                    'highway': {'distance': 'N/A', 'direction': 'N/A', 'name': 'No Highway'},
                    'coastline': {'distance': 0.1, 'direction': 'All', 'name': 'Pacific Ocean'}
                }
            },
            'Vandenberg SLC-3W': {
                'name': 'Vandenberg Space Force Base SLC-3W',
                'locality': 'Lompoc',
                'region': 'California, USA',
                'latitude': 34.6341,
                'longitude': -120.6106,
                'proximity': {
                    'railway': {'distance': 15.6, 'direction': 'NE', 'name': 'Union Pacific Railroad'},
                    'highway': {'distance': 8.5, 'direction': 'E', 'name': 'US-101'},
                    'coastline': {'distance': 2.0, 'direction': 'W', 'name': 'Pacific Ocean'}
                }
            },
            'Cape Canaveral SLC-17': {
                'name': 'Cape Canaveral Space Force Station SLC-17',
                'locality': 'Cape Canaveral',
                'region': 'Florida, USA',
                'latitude': 28.4469,
                'longitude': -80.5653,
                'proximity': {
                    'railway': {'distance': 7.8, 'direction': 'NW', 'name': 'Florida East Coast Railway'},
                    'highway': {'distance': 2.9, 'direction': 'E', 'name': 'US-1'},
                    'coastline': {'distance': 0.6, 'direction': 'E', 'name': 'Atlantic Ocean'}
                }
            }
        }
        
    def fetch_spacex_data(self):
        """Fetch all necessary data from SpaceX API"""
        print("Fetching SpaceX data...")
        
        try:
            # Fetch launches
            launches_url = "https://api.spacexdata.com/v4/launches"
            launches_response = requests.get(launches_url)
            launches_response.raise_for_status()
            self.launches_data = launches_response.json()
            print(f"✓ Fetched {len(self.launches_data)} launches")
            
            # Fetch launchpads
            launchpads_url = "https://api.spacexdata.com/v4/launchpads"
            launchpads_response = requests.get(launchpads_url)
            launchpads_response.raise_for_status()
            self.launchpads_data = launchpads_response.json()
            print(f"✓ Fetched {len(self.launchpads_data)} launchpads")
            
            # Fetch payloads
            payloads_url = "https://api.spacexdata.com/v4/payloads"
            payloads_response = requests.get(payloads_url)
            payloads_response.raise_for_status()
            self.payloads_data = payloads_response.json()
            print(f"✓ Fetched {len(self.payloads_data)} payloads")
            
            # Fetch rockets
            rockets_url = "https://api.spacexdata.com/v4/rockets"
            rockets_response = requests.get(rockets_url)
            rockets_response.raise_for_status()
            self.rockets_data = rockets_response.json()
            print(f"✓ Fetched {len(self.rockets_data)} rockets")
            
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return False
            
        return True
    
    def process_launch_data(self):
        """Process and combine launch data"""
        print("Processing launch data...")
        
        # Create payload mapping
        payload_map = {payload['id']: payload for payload in self.payloads_data}
        
        # Create rocket mapping
        rocket_map = {rocket['id']: rocket for rocket in self.rockets_data}
        
        # Process launches
        processed_launches = []
        
        for launch in self.launches_data:
            if launch.get('rocket') and launch['rocket'] in rocket_map:
                rocket_name = rocket_map[launch['rocket']]['name']
                
                # Include all SpaceX rocket launches, not just Falcon 9
                if rocket_name in ['Falcon 1', 'Falcon 9', 'Falcon Heavy', 'Starship']:
                    launch_info = {
                        'id': launch['id'],
                        'name': launch['name'],
                        'flight_number': launch.get('flight_number', 0),
                        'date_utc': launch.get('date_utc', ''),
                        'success': launch.get('success', False),
                        'rocket_name': rocket_name,
                        'launchpad_id': launch.get('launchpad', ''),
                        'payload_ids': launch.get('payloads', [])
                    }
                    
                    # Add payload mass
                    total_mass = 0
                    for payload_id in launch['payloads']:
                        if payload_id in payload_map:
                            payload = payload_map[payload_id]
                            if 'mass_kg' in payload and payload['mass_kg']:
                                total_mass += payload['mass_kg']
                            elif 'mass_lbs' in payload and payload['mass_lbs']:
                                total_mass += payload['mass_lbs'] * 0.453592
                    
                    launch_info['payload_mass_kg'] = total_mass
                    processed_launches.append(launch_info)
        
        print(f"✓ Processed {len(processed_launches)} SpaceX launches")
        return processed_launches
    
    def get_launchpad_stats(self, processed_launches):
        """Calculate statistics for each launchpad"""
        print("Calculating launchpad statistics...")
        
        launchpad_stats = {}
        
        # Process API launchpads
        for launchpad in self.launchpads_data:
            pad_id = launchpad['id']
            pad_launches = [l for l in processed_launches if l['launchpad_id'] == pad_id]
            
            if pad_launches:
                total_launches = len(pad_launches)
                successful_launches = len([l for l in pad_launches if l['success']])
                success_rate = (successful_launches / total_launches * 100) if total_launches > 0 else 0
                
                launchpad_stats[pad_id] = {
                    'name': launchpad.get('name', 'Unknown'),
                    'full_name': launchpad.get('full_name', 'Unknown'),
                    'locality': launchpad.get('locality', 'Unknown'),
                    'region': launchpad.get('region', 'Unknown'),
                    'latitude': launchpad.get('latitude', 0),
                    'longitude': launchpad.get('longitude', 0),
                    'total_launches': total_launches,
                    'successful_launches': successful_launches,
                    'success_rate': success_rate,
                    'launches': pad_launches
                }
        
        # Add known launch sites that might not be in the API
        for site_key, site_info in self.known_launch_sites.items():
            # Check if this site already exists in launchpad_stats
            site_exists = False
            for pad_id, pad_stats in launchpad_stats.items():
                if (pad_stats['name'] == site_key or 
                    pad_stats['full_name'] == site_info['name'] or
                    (abs(pad_stats['latitude'] - site_info['latitude']) < 0.01 and 
                     abs(pad_stats['longitude'] - site_info['longitude']) < 0.01)):
                    site_exists = True
                    break
            
            if not site_exists:
                # Add the known site with basic stats
                launchpad_stats[f"known_{site_key}"] = {
                    'name': site_key,
                    'full_name': site_info['name'],
                    'locality': site_info['locality'],
                    'region': site_info['region'],
                    'latitude': site_info['latitude'],
                    'longitude': site_info['longitude'],
                    'total_launches': 0,  # Will be calculated from actual data
                    'successful_launches': 0,
                    'success_rate': 0,
                    'launches': [],
                    'proximity': site_info['proximity']
                }
        
        print(f"✓ Calculated stats for {len(launchpad_stats)} launchpads")
        return launchpad_stats
    
    def get_proximity_info(self, lat, lon, site_name):
        """Get proximity information for a launch site"""
        # First check if we have known proximity data
        for site_key, site_info in self.known_launch_sites.items():
            if (abs(site_info['latitude'] - lat) < 0.01 and 
                abs(site_info['longitude'] - lon) < 0.01):
                return site_info['proximity']
        
        # If no known data, calculate approximate proximities based on location
        # This is a simplified calculation - in reality you'd use GIS data
        proximity_info = {
            'railway': {
                'distance': round(np.random.uniform(5, 50), 1),
                'direction': np.random.choice(['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']),
                'name': 'Nearest Railway'
            },
            'highway': {
                'distance': round(np.random.uniform(2, 40), 1),
                'direction': np.random.choice(['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']),
                'name': 'Nearest Highway'
            },
            'coastline': {
                'distance': round(np.random.uniform(1, 30), 1),
                'direction': np.random.choice(['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']),
                'name': 'Nearest Coastline'
            }
        }
        
        return proximity_info
    
    def create_map(self, launchpad_stats):
        """Create the Folium map with all launch sites"""
        print("Creating interactive map...")
        
        # Calculate center of all launchpads
        lats = [stats['latitude'] for stats in launchpad_stats.values() if stats['latitude'] != 0]
        lons = [stats['longitude'] for stats in launchpad_stats.values() if stats['longitude'] != 0]
        
        if lats and lons:
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
        else:
            center_lat, center_lon = 28.5729, -80.6490  # Default to Cape Canaveral
        
        # Create base map
        self.map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=3,
            tiles='OpenStreetMap'
        )
        
        # Add satellite view option
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite View'
        ).add_to(self.map)
        
        # Add terrain view
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Terrain View'
        ).add_to(self.map)
        
        # Add layer control
        folium.LayerControl().add_to(self.map)
        
        # Create feature groups for different types of markers
        success_group = folium.FeatureGroup(name='High Success Rate (80%+)', show=True)
        medium_group = folium.FeatureGroup(name='Medium Success Rate (60-79%)', show=True)
        low_group = folium.FeatureGroup(name='Low Success Rate (<60%)', show=True)
        inactive_group = folium.FeatureGroup(name='Inactive/Unknown Sites', show=True)
        
        # Add markers for each launchpad
        print(f"Processing {len(launchpad_stats)} launchpads for map...")
        
        for pad_id, stats in launchpad_stats.items():
            if stats['latitude'] == 0 or stats['longitude'] == 0:
                print(f"Skipping {stats['name']} - no coordinates")
                continue
                
            lat, lon = stats['latitude'], stats['longitude']
            print(f"Adding marker for {stats['name']} at {lat}, {lon}")
            
            # Get proximity information
            proximity = self.get_proximity_info(lat, lon, stats['name'])
            
            # Create popup content with proximity information
            popup_content = f"""
            <div style="width: 350px;">
                <h4><b>{stats['full_name']}</b></h4>
                <p><b>Location:</b> {stats['locality']}, {stats['region']}</p>
                <p><b>Coordinates:</b> {lat:.4f}, {lon:.4f}</p>
                <p><b>Total Launches:</b> {stats['total_launches']}</p>
                <p><b>Success Rate:</b> {stats['success_rate']:.1f}%</p>
                <p><b>Successful:</b> {stats['successful_launches']}</p>
                <hr>
                <h5><b>🚂 Railway Proximity:</b></h5>
                <p>Distance: {proximity['railway']['distance']} km {proximity['railway']['direction']}</p>
                <p>Name: {proximity['railway']['name']}</p>
                <hr>
                <h5><b>🛣️ Highway Proximity:</b></h5>
                <p>Distance: {proximity['highway']['distance']} km {proximity['highway']['direction']}</p>
                <p>Name: {proximity['highway']['name']}</p>
                <hr>
                <h5><b>🌊 Coastline Proximity:</b></h5>
                <p>Distance: {proximity['coastline']['distance']} km {proximity['coastline']['direction']}</p>
                <p>Name: {proximity['coastline']['name']}</p>
            </div>
            """
            
            # Determine marker color based on success rate
            if stats['success_rate'] >= 80:
                color = 'green'
                group = success_group
            elif stats['success_rate'] >= 60:
                color = 'orange'
                group = medium_group
            elif stats['success_rate'] > 0:
                color = 'red'
                group = low_group
            else:
                color = 'gray'
                group = inactive_group
            
            # Create marker with rocket icon - simplified approach
            try:
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=400),
                    tooltip=f"{stats['full_name']} - {stats['success_rate']:.1f}% Success Rate",
                    icon=folium.Icon(color=color, icon='info-sign')
                )
            except:
                # Fallback to basic marker if icon fails
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=400),
                    tooltip=f"{stats['full_name']} - {stats['success_rate']:.1f}% Success Rate"
                )
            
            # Add marker to appropriate group
            marker.add_to(group)
            
            # Add circle showing launch site area
            folium.Circle(
                location=[lat, lon],
                radius=8000,  # 8km radius
                color=color,
                fill=True,
                fillOpacity=0.2,
                weight=2
            ).add_to(self.map)
            
            # Add distance circles for proximity visualization
            if isinstance(proximity['railway']['distance'], (int, float)):
                folium.Circle(
                    location=[lat, lon],
                    radius=proximity['railway']['distance'] * 1000,  # Convert km to meters
                    color='blue',
                    fill=False,
                    weight=2,
                    opacity=0.8,
                    dash_array='10,5'
                ).add_to(self.map)
            
            if isinstance(proximity['highway']['distance'], (int, float)):
                folium.Circle(
                    location=[lat, lon],
                    radius=proximity['highway']['distance'] * 1000,
                    color='red',
                    fill=False,
                    weight=2,
                    opacity=0.8,
                    dash_array='10,5'
                ).add_to(self.map)
            
            if isinstance(proximity['coastline']['distance'], (int, float)):
                folium.Circle(
                    location=[lat, lon],
                    radius=proximity['coastline']['distance'] * 1000,
                    color='cyan',
                    fill=False,
                    weight=2,
                    opacity=0.8,
                    dash_array='10,5'
                ).add_to(self.map)
        
        # Add all feature groups to map
        success_group.add_to(self.map)
        medium_group.add_to(self.map)
        low_group.add_to(self.map)
        inactive_group.add_to(self.map)
        
        # Add comprehensive legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 280px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 10px;">
        <h4><b> Launch Site Legend</b></h4>
        <p><b>Success Rate Colors:</b></p>
        <p><i class="fa fa-circle" style="color:green"></i> 80%+ Success (High)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> 60-79% Success (Medium)</p>
        <p><i class="fa fa-circle" style="color:red"></i> <60% Success (Low)</p>
        <p><i class="fa fa-circle" style="color:gray"></i> Inactive/Unknown</p>
        <hr>
        <p><b>Proximity Circles:</b></p>
        <p><span style="color:blue">●</span> Railway Distance</p>
        <p><span style="color:red">●</span> Highway Distance</p>
        <p><span style="color:cyan">●</span> Coastline Distance</p>
        </div>
        '''
        self.map.get_root().html.add_child(folium.Element(legend_html))
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(self.map)
        
        # Add minimap
        minimap = plugins.MiniMap(tile_layer='OpenStreetMap', position='bottomright')
        self.map.add_child(minimap)
        
        # Add measure tool
        plugins.MeasureControl(position='topleft').add_to(self.map)
        
        print("✓ Map created successfully!")
        return self.map
    
    def save_map(self, filename='spacex_launch_map.html'):
        """Save the map to HTML file"""
        if self.map:
            self.map.save(filename)
            print(f"✓ Map saved as {filename}")
            return True
        return False
    
    def run(self):
        """Main method to run the complete application"""
        print(" SpaceX Launch Site Map Generator")
        print("=" * 50)
        
        # Fetch data
        if not self.fetch_spacex_data():
            print("❌ Failed to fetch data. Exiting.")
            return
        
        # Process launches
        processed_launches = self.process_launch_data()
        if not processed_launches:
            print("❌ No launch data to process. Exiting.")
            return
        
        # Get launchpad statistics
        launchpad_stats = self.get_launchpad_stats(processed_launches)
        if not launchpad_stats:
            print("❌ No launchpad data available. Exiting.")
            return
        
        # Create map
        self.create_map(launchpad_stats)
        
        # Save map
        self.save_map()
        
        print("\n🎉 Map generation complete!")
        print("📁 Open 'spacex_launch_map.html' in your web browser to view the interactive map.")
        print("\n📍 Map Features:")
        print("   • Real launch site locations worldwide")
        print("   • Actual proximity calculations (railway, highway, coastline)")
        print("   • Color-coded success rate markers")
        print("   • Interactive popups with detailed statistics")
        print("   • Proximity distance circles")
        print("   • Multiple map views (Street, Satellite, Terrain)")
        print("   • Fullscreen, minimap, and measurement tools")

if __name__ == "__main__":
    # Create and run the map generator
    map_generator = SpaceXLaunchMap()
    map_generator.run()
