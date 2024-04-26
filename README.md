The project is inspired by "UrbanAlliance - ECON Capstone Idea - PTN Gap Analysis" pdf.

"
Problem Statement: 
This project will assess the planned investments in the Primary Transit Network against socio-economic variables to determine if there are gaps or adjustments necessary. Students may consider variables such as socio-economic profiles of individuals/households or other equity seeking groups which may rely disproportionately on transit for their mobility (lower-income households, new/recent immigrants, service sector employment, affordable housing).
"

Process:

For the project, we assessed through the typical economic method: Demand of the Calgarians and the current and future Supply of Calgary's Primary Transit Network (consisting of Max buses and transit line). Based on the literature we found on the topic, the demand index was calculated based on 4 factors/groups:
Seniors: The demographic of people that are from 65 years old and over.
Low Income: The demographic of people or household that make <= $26,503.
Household Income on Rent: The demographic of people who spend more than 30% of their income on rent.
Transit for Work: The demographic of employees who are using transit to commute to work.

For Supply, there were 3 categories we considered for the network:
Service Coverage: It measures how well the transit stops are serving the community. It is calculated by the amount of stops in a community divided by the community's population.
Service Frequency: It measures how frequently the transit moves in a given day.
Service Capacity: It measures the total number of people a transit can fit per trip.

Once we have both sides, transit gap will be assessed by the difference of Demand and Supply. The results for all will be visualized using ArcGIS and Python library 'Streamlit'.

Procedure:

Demand:
- Web scraping Community Profiles from "https://www.calgary.ca/communities/profiles.html" using Python.
- Converting the pdf files to text and from text to CSV to get a combined profile.
- Use the CSV and calculate demand based on the factors mentioned above.
    - Calculated based on this formula: TDI = SS (lowincome*wli + seniors*ws + greaterthan30%*wg30 + transitusers*wtu)
    - SS = (X-Xmin)/(Xmax-Xmin)
- Optional:
    - Display top 5 and bottom 5 of the communities on the list.
    - Letter Grades for easier interpretation

Supply:
- Get GTFS data file for Calgary Transit (as updated it can be)
- Use GTFS library in Python to extract data from the data file
- Input: Time window, Type of frequency (Lines, Stops etc.)
- Lines Frequency: Data that shows how many times a certain transit has traveled over the time period of the day.
- From the data, extract total number of trips and frequency of the trip between one another.
- Stops file that shows community names where the stops are and what transit goes through there.
- Use the stops file to create database which contains number of trips and frequency of the trips.
- The formula: 𝑇𝑆𝐼=(𝑆𝑆(𝑍𝑠𝑒𝑟𝑣𝑖𝑐𝑒𝑓𝑟𝑒𝑞+𝑍𝑠𝑒𝑟𝑣𝑖𝑐𝑒𝑐𝑜𝑣+𝑍𝑠𝑒𝑟𝑣𝑖𝑐𝑒𝑐𝑎𝑝))/3
    - SS = (X-Xmin)/(Xmax-Xmin)
- From the database, calculate frequency and capacity index.
- Service Coverage index would have to be calculated using ArcGIS Pro
- Merge both and calculate supply index using the formula above, matching it based on community names.
- Optional:
    - Display top 5 and bottom 5 of the communities on the list.
    - Letter Grades for easier interpretation

Gap:
- Merge Demand index and Supply index data matching with community names and calculating the gap.
- Formula: Gap = Demand - Supply
- Optional:
    - Display top 5 and bottom 5 of the communities on the list.
    - Letter Grades for easier interpretation
