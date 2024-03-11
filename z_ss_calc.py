import pandas as pd
import os

community_data_path = os.getcwd()+"/Data Sets/Analysis Data/Community Profiles Compiled.xlsx"
comm_df = pd.read_excel(community_data_path)
comm_df.head()
#Z-Score method manually
pop_mean = comm_df['Population in private households'].mean()
pop_std = comm_df['Population in private households'].std()
# pop_max = comm_df['Population in private households'].max()
# pop_min = comm_df['Population in private households'].min()

medinc_mean = comm_df["Median household income of private households"].mean()
medinc_std = comm_df["Median household income of private households"].std()
# medinc_max = comm_df['Median household income of private households'].max()
# medinc_min = comm_df['Median household income of private households'].min()

low_mean = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].mean()
low_std = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].std()
# low_max = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].max()
# low_min = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].min()

trans_mean = ((comm_df["Population in private households"]/comm_df["Employed labour force aged 15 years and over in private households"])*comm_df['Public transit']).mean()
trans_std = ((comm_df["Population in private households"]/comm_df["Employed labour force aged 15 years and over in private households"])*comm_df['Public transit']).std()
# trans_max = ((comm_df["Population in private households"]/comm_df["Employed labour force aged 15 years and over in private households"])*comm_df['Public transit']).max()
# trans_min = ((comm_df["Population in private households"]/comm_df["Employed labour force aged 15 years and over in private households"])*comm_df['Public transit']).min()

rent_mean = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].mean()
rent_std = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].std()
# rent_max = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].max()
# rent_min = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'].min()
row, col = comm_df.shape
z_rows_to_append = []
for c in range(row):
    community = comm_df['Community Name'][c]
    
    pop = comm_df['Population in private households'][c]
    # pop_ss = (pop-pop_max)/(pop_max-pop_min)
    z_pop_score = (pop-pop_mean)/pop_std
    
    med = comm_df['Median household income of private households'][c]
    # med_ss = (med-medinc_max)/(medinc_max-medinc_min)
    z_med_score = (med-medinc_mean)/medinc_std
    
    trans = ((comm_df["Population in private households"]/comm_df["Employed labour force aged 15 years and over in private households"])*comm_df['Public transit'])[c]
    # trans_ss = (trans-trans_max)/(trans_max-trans_min)
    z_trans_score = (trans-trans_mean)/trans_std
    
    rent = comm_df['Per cent households with income spending 30% or more total income on shelter (Renter)'][c]
    # rent_ss = (rent-rent_max)/(rent_max-rent_min)
    z_rent_score = (rent-rent_mean)/rent_std
    
    low = comm_df['Population in private households to whom low income concepts are applicable (Number in low income)'][c]
    # low_ss = (low-low_max)/(low_max-low_min)
    z_low_score = (low-low_mean)/low_std

    z_result = z_pop_score+z_trans_score+z_rent_score+z_low_score-z_med_score

    column_df = {"Community Name": community, "Z Score": z_result}
    z_rows_to_append.append(column_df)


Z_index_df = pd.DataFrame(z_rows_to_append)
z_max = Z_index_df['Z Score'].max()
z_min = Z_index_df['Z Score'].min()
row, col = Z_index_df.shape
z_ss_rows = []
for c in range(row):
    community = Z_index_df["Community Name"][c]
    z_score = Z_index_df['Z Score'][c]

    z_ss_result = (z_score-z_max)/(z_max-z_min)

    column_df = {"Community Name": community, "Z Score": z_ss_result}
    z_ss_rows.append(column_df)
    
z_ss_index_df = pd.DataFrame(z_ss_rows)
