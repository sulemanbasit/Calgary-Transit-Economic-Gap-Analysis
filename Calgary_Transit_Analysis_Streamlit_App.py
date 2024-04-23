import streamlit as st
import pandas as pd
import json
import plotly.express as px
from fractions import Fraction

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

# Main Streamlit app layout
def main():
    st.title("Calgary Transit Analysis")

    # Input fields for weights
    st.header("Weight Input for Analysis")
    low_income_weight = st.text_input("Enter weight for Low income (between 0 and 1):", '0.25')
    seniors_weight = st.text_input("Enter weight for Seniors (between 0 and 1):", '0.25')
    rent_weight = st.text_input("Enter weight for Rent (between 0 and 1):", '0.25')
    public_transit_weight = st.text_input("Enter weight for Public transit (between 0 and 1):", '0.25')

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

            # Display data table
            st.write("Calculated Indices", df[['Low Income Index', 'Seniors Index', 'Rent Index', 'Public Transit Index']])

            # Load Demand file and Geojson file and match communities coordinates with their standardized demand index
            Demand_index_df = pd.read_csv('TotalDemandIndexStandardizedMethod2.csv')
            with open('Census by Community 2019_20240401 copy.geojson', 'r') as file:
                geojson_data = json.load(file)

            # Create the name mapping from the CSV data
            name_mapping = {row['Community Name']: row['Standardized Total Community Index'] for index, row in Demand_index_df.iterrows()}

            # Filter through the geojson file and organize the communities by their standardized demand
            community_geojson = {
                "type": "FeatureCollection",
                "features": [f for f in geojson_data['features'] if f['properties']['name'] in name_mapping]
            }

            # Update feature properties with the standardized index
            for feature in community_geojson['features']:
                feature['properties']['Standardized Index'] = name_mapping[feature['properties']['name']]

            # Create a map that displays the demand index score for a community
            fig = px.choropleth(community_geojson, 
                                geojson=community_geojson, 
                                locations=[f['properties']['name'] for f in community_geojson['features']],
                                featureidkey="properties.name",
                                color=[f['properties']['Standardized Index'] for f in community_geojson['features']],
                                projection="mercator",
                                color_continuous_scale="Viridis")  # Optional: Choose a color scale

            # Update the layout with a title and color axis label
            fig.update_layout(
                title_text='Demand Index',  # Set the title of the map
                geo=dict(
                    showframe=False,  # Remove the frame around the map
                    showcoastlines=False  # Remove coastlines (if not relevant)
                ),
                coloraxis_colorbar=dict(title='Standardized Demand Index')  # Set the title for the color scale
            )

            fig.update_geos(fitbounds="locations")
            st.plotly_chart(fig)
        except Exception as e:
            st.error(str(e))  # Corrected to properly display the exception message

if __name__ == "__main__":
    main()
