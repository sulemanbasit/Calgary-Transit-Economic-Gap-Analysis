import streamlit as st
import pandas as pd
import json
import plotly.express as px
from fractions import Fraction
import numpy as np
import matplotlib.pyplot as mpt
import os
import geopandas as gpd
from glob import glob
from gtfs_functions import Feed


gtfs_path = "OneDrive_1_4-6-2024.zip" #update this if needed
current_stops_data = "Stops_Sorted (1).xlsx"
future_stops_data = "Stops_Sorted_Future_Network.xlsx"
current_cov = 'PTN service coverage.csv'
future_cov = 'Future Transit Service Coverage.csv'
demand_2 = "TotalDemandIndexStandardizedMethod2.csv"
comm_file = 'demand.csv'
census_file = "Census by Community 2019_20240401 copy.geojson"
red_code = '201-20718'
blue_code = '202-20718'
orange_code = '303-20727'
yellow_code = '304-20727'
teal_code = '306-20727'
purple_code = '307-20727'
comm_list = []
red_list = []
blue_list = []
orange_list = []
yellow_list = []
purple_list = []
teal_list = []


#def assign_grade(score):
    #for grade, boundary in grade_boundaries.items():
    #    if score >= boundary:
    #        return grade
   # return 'F'

def assign_time(time_list):
    time_format_list = [t+':00' for t in time_list]
    return time_format_list

# Function to validate weight input
def get_valid_weight(weight):
    if '/' in weight:
        weight = float(Fraction(weight))
    else:
        weight = float(weight)
    if not 0 <= weight <= 1:
        raise ValueError("Weight must be a number between 0 and 1")
    return weight

# Function to calculate and check the sum of weights
def validate_weights(weights):
    total = sum(weights)
    if not abs(total - 1) < 1e-10:
        raise ValueError("Error: The sum of weights must be equal to 1. Please try again.")
    return weights

# Function to assign grades based on index values
def assign_grades(value):
    if value > 0.8:
        return 'A'
    elif value > 0.6:
        return 'B'
    elif value > 0.4:
        return 'C'
    elif value > 0.2:
        return 'D'
    else:
        return 'F'
# Main Streamlit app layout
def main():
    st.title("Calgary Transit Analysis")

    # Input fields for weights
    st.header("User Input for Analysis")
    low_income_weight = st.text_input("Enter weight for Low income (between 0 and 1):", '0.25')
    seniors_weight = st.text_input("Enter weight for Seniors (between 0 and 1):", '0.25')
    rent_weight = st.text_input("Enter weight for Rent (between 0 and 1):", '0.25')
    public_transit_weight = st.text_input("Enter weight for Public transit (between 0 and 1):", '0.25')
    train_capacity = st.number_input('Enter train capacity', value=600)
    bus_capacity = st.number_input('Enter bus capacity', value=65)
    t = st.text_input("Input time range and separate by comma (eg. 6am-9am: 6,7,8,9):")
    if st.button("Calculate Indices"):
        try:
            # Validate and convert weights
            weights = validate_weights([
                get_valid_weight(low_income_weight),
                get_valid_weight(seniors_weight),
                get_valid_weight(rent_weight),
                get_valid_weight(public_transit_weight)
            ])

            # Load and process data
            excel_file = "Community Profiles Compiled.xlsx"  # This path will need to be adjusted to where the file is hosted
            df = pd.read_excel(excel_file)

            # Calculating indices based on weights
            df['Low Income Index'] = df['Population in private households to whom low income concepts are applicable (Number in low income)'] * weights[0]
            df['Seniors Index'] = df['Seniors'] * weights[1]
            df['Rent Index'] = df['Spend more than 30% on rent'] * weights[2]
            df['Public Transit Index'] = df['Public transit'] * weights[3]
            df['Total Community Index']=df['Low Income Index']+df['Seniors Index']+df['Rent Index']+df['Public Transit Index']
            max_total=df['Total Community Index'].max()
            min_total=df['Total Community Index'].min()
            df['Standardized Total Community Index']=(df['Total Community Index']-min_total)/(max_total-min_total)
            df['Grade'] = df['Standardized Total Community Index'].apply(assign_grades)
            Index=['Community Name','Low Income Index','Seniors Index','Rent Index','Public Transit Index','Total Community Index','Standardized Total Community Index','Grade']
            df=df.filter(Index)
            pd.set_option('display.max_rows',None)
            df.to_csv('TotalDemandIndexStandardizedMethod2.csv',index=False)

            # Display calculated index for each group by community 
            st.write("Calculated Indices", df[['Community Name', 'Low Income Index', 'Seniors Index', 'Rent Index', 'Public Transit Index']])
            
            # Sort data by Standardized Total Community Index and select top 5 and bottom 5
            df_sorted = pd.read_csv('TotalDemandIndexStandardizedMethod2.csv')
            df_sorted = df.sort_values(by='Standardized Total Community Index', ascending=False)
            top_5 = df_sorted.head(5)
            bottom_5 = df_sorted.tail(5)
            
            # Display top 5 and bottom 5 communities
            st.write("Top 5 Communities by Standardized Index", top_5[['Community Name', 'Standardized Total Community Index']])
            st.write("Bottom 5 Communities by Standardized Index", bottom_5[['Community Name', 'Standardized Total Community Index']])

            
            # Load Demand file and Geojson file and match communities coordinates with their standardized demand index
            Demand_index_df = pd.read_csv('TotalDemandIndexStandardizedMethod2.csv')
            with open('Census by Community 2019_20240401 copy.geojson', 'r') as file:
                geojson_data = json.load(file)

            name_mapping = {row['Community Name']: row['Grade'] for index, row in Demand_index_df.iterrows()}

            # Filter through the geojson file and organize the communities by their standardized demand
            community_geojson = {
                "type": "FeatureCollection",
                "features": [f for f in geojson_data['features'] if f['properties']['name'] in name_mapping]
            }

            # Update feature properties with the standardized index
            for feature in community_geojson['features']:
                feature['properties']['Grade'] = name_mapping[feature['properties']['name']]

            # Create a map that displays the demand index score for a community
            fig = px.choropleth(community_geojson, 
                                geojson=community_geojson, 
                                locations=[f['properties']['name'] for f in community_geojson['features']],
                                featureidkey="properties.name",
                                color=[f['properties']['Grade'] for f in community_geojson['features']],
                                projection="mercator",
                                color_discrete_map={"A": "green", "B": "blue", "C": "yellow", "D": "orange", "F": "red"})

            # Update the layout with a title and color axis label
            fig.update_layout(
                title_text='Demand Index',  # Set the title of the map
                geo=dict(
                    showframe=False,  
                    showcoastlines=False  
                ),
                coloraxis_colorbar=dict(title='Standardized Demand Index Grades')  # Set the title for the color scale
            )
            fig.update_geos(fitbounds="locations")
            st.plotly_chart(fig)
            
            t_l = t.split(',')
            time_range_list = assign_time(t_l)
            pattern = '|'.join(time_range_list)
            feed = Feed(gtfs_path, time_windows=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
            line_freq = feed.lines_freq
            ptn = line_freq.loc[line_freq["route_name"].str.contains("Line|MAX")].sort_values(by=['window'])
            input_hour_performance = ptn.loc[ptn['window'].str.contains(pattern)].sort_values(by=['route_name'])
            n_trips = input_hour_performance.groupby('route_id')['ntrips'].sum()
            mean_min_per_trip = input_hour_performance.groupby('route_id')['min_per_trip'].mean()
            median_min_per_trip = input_hour_performance.groupby('route_id')['min_per_trip'].median()
            blue_trips = n_trips.loc[blue_code]
            blue_freq = median_min_per_trip.loc[blue_code]
            red_trips = n_trips.loc[red_code]
            red_freq = median_min_per_trip.loc[red_code]
            orange_trips = n_trips.loc[orange_code]
            orange_freq = median_min_per_trip.loc[orange_code]
            teal_trips = n_trips.loc[teal_code]
            teal_freq = median_min_per_trip.loc[teal_code]
            yellow_trips = n_trips.loc[yellow_code]
            yellow_freq = median_min_per_trip.loc[yellow_code]
            purple_trips = n_trips.loc[purple_code]
            purple_freq = median_min_per_trip.loc[purple_code]
            comm_data = pd.read_csv(comm_file)
            stop_df = pd.read_excel(current_stops_data, sheet_name = "Sheet2")
            stop_df['Community'] = stop_df['Community'].str.rstrip('\n').str.replace('\n',',')
            for index, row in stop_df.iterrows():
                if 'Line' in row['Line']:
                    if 'Red' in row['Line']:
                        red_list.extend([com for com in row['Community'].split(',')])
                    else:
                        blue_list.extend([com for com in row['Community'].split(',')])
            else:
                if 'Orange' in row['Line']:
                    orange_list.extend([com for com in row['Community'].split(',')])
                elif 'Purple' in row['Line']:
                    purple_list.extend([com for com in row['Community'].split(',')])
                elif 'Teal' in row['Line']:
                    teal_list.extend([com for com in row['Community'].split(',')])
                else:
                    yellow_list.extend([com for com in row['Community'].split(',')])
            
            comm_list = list(set(red_list+blue_list+orange_list+purple_list+teal_list+yellow_list))
            clean_com_list = [item for item in comm_list if item.strip()]
            service_df = pd.DataFrame(clean_com_list, columns=["Community"]).sort_values(by="Community")

            service_df["Red Trips"] = service_df["Community"].isin(red_list) * red_trips
            service_df["Red Freq"] = service_df["Community"].isin(red_list) * red_freq
            service_df["Blue Trips"] = service_df["Community"].isin(blue_list) * blue_trips
            service_df["Blue Freq"] = service_df["Community"].isin(blue_list) * blue_freq
            service_df["Orange Trips"] = service_df["Community"].isin(orange_list) * orange_trips
            service_df["Orange Freq"] = service_df["Community"].isin(orange_list) * orange_freq
            service_df["Yellow Trips"] = service_df["Community"].isin(yellow_list) * yellow_trips
            service_df["Yellow Freq"] = service_df["Community"].isin(yellow_list) * yellow_freq
            service_df["Teal Trips"] = service_df["Community"].isin(teal_list) * teal_trips
            service_df["Teal Freq"] = service_df["Community"].isin(teal_list) * teal_freq
            service_df["Purple Trips"] = service_df["Community"].isin(purple_list) * purple_trips
            service_df["Purple Freq"] = service_df["Community"].isin(purple_list) * purple_freq

# Merge the two DataFrames on the 'Community' and 'Community Name' columns
            merged_data = pd.merge(service_df, comm_data, left_on='Community', right_on='Community Name', how='right')

# Update the 'Population' column in sup_fc with the corresponding values from comm_data
            service_df['Population'] = service_df['Community'].apply(
                lambda x: merged_data.loc[merged_data['Community Name'] == x, 'Population in private households'].iloc[0]
                if x in merged_data['Community Name'].tolist() else 0
)

# dropping rows that have no population:
            service_df = service_df[service_df['Population'] != 0]

# Calculate Index
            service_df["Frequency Index"] = service_df.filter(like="Freq").sum(axis=1)
            service_df['Total Trips'] = service_df.filter(regex="Red Trips|Blue Trips").sum(axis=1)*train_capacity + service_df.filter(regex="Orange Trips|Yellow Trips|Teal Trips|Yellow Trips|Purple Trips").sum(axis=1)*bus_capacity
            service_df["Capacity Index"] = service_df['Total Trips']/service_df.filter(like='Population').sum(axis=1)

            min_freq = min(service_df['Frequency Index'])
            max_freq = max(service_df['Frequency Index'])
            min_cap = min(service_df['Capacity Index'])
            max_cap = max(service_df['Capacity Index'])

            service_df['SS Frequency Index'] = (service_df['Frequency Index']-min_freq)/(max_freq-min_freq)
            service_df['SS Capacity Index'] = (service_df['Capacity Index']-min_cap)/(max_cap-min_cap)
            curr_cov_file = pd.read_csv(current_cov)

            supply_df_upper = service_df.copy()
            supply_df_upper['Community'] = supply_df_upper['Community'].str.upper()

            merged_data = pd.merge(supply_df_upper, curr_cov_file, how='right', left_on='Community', right_on='NAME')

            final_supply = merged_data[['NAME','SS Frequency Index','SS Capacity Index','SS_Ser_Cov']]

            final_supply = final_supply.rename(columns={'SS_Ser_Cov':"SS Coverage Index"})
            final_supply = final_supply.fillna(0)

            final_supply['Average Supply Index'] = final_supply[['SS Frequency Index','SS Capacity Index','SS Coverage Index']].mean(axis=1)
            demand_df = pd.read_csv(demand_2)
            demand_df['Community Name'] = demand_df['Community Name'].str.upper()
            dns_merge = pd.merge(final_supply,demand_df, how='right', left_on='NAME', right_on='Community Name')

            final_current_df = dns_merge[['NAME',"Low Income Index","Seniors Index","Rent Index","Total Community Index", "SS Frequency Index", "SS Capacity Index",'SS Coverage Index',"Standardized Total Community Index","Average Supply Index"]]
            final_current_df = final_current_df.rename(columns={'Standardized Total Community Index': 'Community Demand Index'})
            final_current_df = final_current_df.fillna(0)

            final_current_df["Transit Gap"] = final_current_df['Community Demand Index'] - final_current_df['Average Supply Index']

            percentiles = final_current_df['Transit Gap'].quantile([0.2,0.4,0.6,0.8])

            grade_boundaries = { # Create percentiles to assign proper letter grade
                'A': percentiles[0.8],  # Top 20% get an 'A'
                'B': percentiles[0.6],  # Next 20% get a 'B'
                'C': percentiles[0.4],  # Next 20% get a 'C'
                'D': percentiles[0.2],  # Next 20% get a 'D'
                'F': 0                   # Bottom 20% get an 'F'
}
            final_current_df['Letter Grade'] = final_current_df['Transit Gap'].apply(assign_grades)

            comm_geo = gpd.read_file(census_file)
            dns_bound_data = pd.merge(final_current_df, comm_geo, how='left', left_on='NAME', right_on='name')
            current_dns = gpd.GeoDataFrame(dns_bound_data[['name',"Low Income Index","Seniors Index","Rent Index","Total Community Index", "SS Frequency Index", "SS Capacity Index",'SS Coverage Index',"Community Demand Index","Average Supply Index",'Transit Gap','Letter Grade','geometry']])
            
            current_dns.to_file('final_data_set', driver='GeoJSON')
            with open('final_data_set.geojson', 'r') as file:
                    geojson_data = json.load(file)
            
            st.write('reach this point')
#-------------
            fig2 = px.choropleth(
            geojson=geojson_data,
            featureidkey="properties.NAME",
            locations=[feature['properties']['NAME'] for feature in geojson_data['features']],
            color=[feature['properties']['Average Supply Index'] for feature in geojson_data['features']],
            color_continuous_scale="Viridis",
            title="Supply Index",
            labels={"color": "Average Supply Index"}
)


            fig2.update_geos(fitbounds="locations", visible=False)

            
            st.plotly_chart(fig2)


            fig3 = px.choropleth(
            geojson=geojson_data,
            featureidkey="properties.NAME",
            locations=[feature['properties']['NAME'] for feature in geojson_data['features']],
            color=[feature['properties']['Transit Gap'] for feature in geojson_data['features']],
            color_continuous_scale="Viridis",
            title="Transit Gap",
            labels={"color": "Transit Gap"}
)


            fig3.update_geos(fitbounds="locations", visible=False)


            st.plotly_chart(fig3)

        except Exception as e:
            st.error(str(e))  

if __name__ == "__main__":
    main()