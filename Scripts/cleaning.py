# uncomment the following 3 lines to install the packages
# !pip install numpy
# !pip install pandas
# !pip install warnings

### Import pandas and numpy libraries

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

### Read all the required files into separate Dataframes
df = pd.read_csv("../Data/places.csv", encoding = 'ISO-8859-1')
df_melbourne = pd.read_csv("../Data/Greater melbourne region.csv", encoding = 'ISO-8859-1')
df_sport= pd.read_csv("../Data/SportandRec.csv", encoding =  'ISO-8859-1')
df_mel = pd.read_csv("../Data/places_of_interest.csv")
df_lib = pd.read_csv("../Data/libraries.csv")
suburb = pd.read_csv("../Data/suburbs.csv")


# Filter out data pertaining to greater melbourne region alone
df_melbourne["Greater melbourne council"] = df_melbourne["Greater melbourne council"].str.upper()
mel = pd.merge(df, df_melbourne, how = 'inner', left_on ="Municipality", right_on = "Greater melbourne council")
df_sport = pd.merge(df_sport, df_melbourne, how = 'inner', left_on ="LGA", right_on = "Greater melbourne  LGA")
suburbs_mel = pd.merge(df_melbourne, suburb, how = 'inner', left_on ="Municipality Names", right_on = "Municipality Name")[["Locality Name", "Municipality Name"]]
df_lib =pd.merge(df_lib, suburbs_mel, how = 'inner', left_on ="Suburb/Town", right_on = "Locality Name")


# Group the data based on interest
gb = mel.groupby('Feature Type')[["Feature Type","Municipality","Place Name", "Longitude", "Latitude", "Historical Information", "Url"]]   
dfs = {}

for x in gb.groups:
    dfs[x] = gb.get_group(x)

# Club similar types into broader categories
dfs["Historic"] = dfs["HISTORIC SITE"].append(dfs["MONUMENT"]).append(dfs["BEACH"]).append(dfs["FARM"]).append(dfs["LAKE"]).append(dfs["FERRY STATION"])
dfs["PARKS"] = dfs["BOTANIC GARDENS"].append(dfs["NATIONAL PARK"]).append(dfs["PARK"])
dfs["SPORTS"] = dfs["SPORT FACILITY"].append(dfs["SPORTS COMPLEX"]).append(dfs["SWIMMING POOL"]).append(dfs["RACECOURSE"]).append(dfs["PLAYGROUND"]).append(dfs["CAMP GROUND"])


# filtering out unwanted categories from the melbourne data
df_mel.rename(columns={"Feature Name": "Place Name"}, inplace=True)
retain_list = ["Community Use", "Leisure/Recreation", "Place of Assembly", "Place of Worship"]
df_mel = df_mel[df_mel.Theme.isin(retain_list)]

# club into broader categories based on similarity
gb1 = df_mel.groupby('Theme')   
dfs1 = {}

for x in gb1.groups:
    dfs1[x] = gb1.get_group(x)
    
dfs1["Community Use"] = dfs1["Community Use"][dfs1["Community Use"]["Sub Theme"].isin(["Public Buildings", "Visitor Centre"])]

# ------------------------------------------------------------------------------------------- SPORTS --------------------------------------------------------------------------------------------------
# Create address for sports and drop all other columns
df_sport.drop(columns=["X", "Y", "OBJECTID", "Facility_ID", "FaciltySportPlayedID", "Greater melbourne council","LGA_y","Greater melbourne  LGA","Municipality Names"], inplace=True)
df_sport[["StreetNo","Postcode"]] = df_sport[["StreetNo","Postcode"]].fillna(0)
df_sport['StreetNo'] = df_sport['StreetNo'].astype(str)
df_sport['Postcode'] = df_sport['Postcode'].astype(int).astype(str)
df_sport.StreetNo.replace("0"," ", inplace=True)
df_sport.Postcode.replace("0"," ", inplace=True)

df_sport ["Address"] = df_sport["StreetNo"] + " " + df_sport["StreetName"]+ " " + df_sport["StreetType"]+ " " + df_sport["SuburbTown"]+ " " + df_sport["Postcode"] 
df_sport.Address = df_sport.Address.str.strip()
df_sport.drop(columns=["StreetNo", "StreetName", "StreetType", "SuburbTown", "Postcode"], inplace=True)


# sports from melbourne data
sport = dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"].isin(['Major Sports & Recreation Facility','Private Sports Club/Facility', 'Gymnasium/Health Club'])].rename(columns = {"Sub Theme": "SportsPlayed", "Place Name": "FacilityName"}).drop(columns=["Theme"])


# sports from vic data tool - formatting
dfs["SPORTS"]["Municipality"] = dfs["SPORTS"]["Municipality"].str.title()
dfs["SPORTS"]["Place Name"] = dfs["SPORTS"]["Place Name"].str.title()
dfs["SPORTS"]["Feature Type"] = dfs["SPORTS"]["Feature Type"].str.title()


# add categories / tags rename columns and drop unwanted columns for all the 3 dataframes
dfs["SPORTS"]["Categories"] = [["Sports", i] for i in dfs["SPORTS"]["Feature Type"]]
dfs["SPORTS"].drop(columns = ["Feature Type"], inplace = True)

df_sport["Categories"] = [["Sport", i] for i in df_sport["SportsPlayed"]]
df_sport.drop(columns = ["FacilityAge", "FacilityUpgradeAge"], inplace = True)
df_sport.rename(columns={"LGA_x":"Municipality", "FacilityName":"Place Name", "SportsPlayed":"Sports Played", "NumberFieldCourts":"Number of Field Courts", "FieldSurfaceType": "Field Surface Type", "FacilityCondition": "Facility Condition"}, inplace = True)

df_sport["Municipality"] = df_sport["Municipality"].str.title()

sport["Categories"] = [["Sport", "Sports Facility"] if i =="Major Sports & Recreation Facility" else ["Sport", "Sports Facility", "Private"] if i =="Private Sports Club/Facility" else ["Sports"] for i in sport["SportsPlayed"]]
category_list = ["Park","Racecourse", "Football", "Basketball", "Netball", "Cricket", "Golf", "Tennis", "Hockey", "Shooting", "Gymnasium"]

for i in range(len(sport)):
    for j in category_list:
        if j in sport["FacilityName"].iloc[i]:
            sport["Categories"].iloc[i] = sport["Categories"].iloc[i] + [j]
        
sport.rename(columns = {"FacilityName":"Place Name"}, inplace = True)
sport.drop(columns = ["SportsPlayed"], inplace = True)

# join all the dataframes together
df_sports = df_sport.append(sport).append(dfs["SPORTS"])

# drop duplicates
df_sports.drop_duplicates(subset = ["Place Name"], inplace = True)

# write to file
df_sports.to_csv("../Data/Output files/Sports.csv", index = False)

# ------------------------------------------------------------------------------------------- TOURIST --------------------------------------------------------------------------------------------------

# data from vic data tool - formatting
dfs["Historic"]["Feature Type"] = dfs["Historic"]["Feature Type"].str.title()
dfs["Historic"]["Municipality"] = dfs["Historic"]["Municipality"].str.title()
dfs["Historic"]["Place Name"] = dfs["Historic"]["Place Name"].str.title()

# add categories
dfs["Historic"]["Categories"] = [["Tourist place of interest", i] for i in dfs["Historic"]["Feature Type"]]

# data from melbourne, join similar types, add categories and format
dfs1["Community Use"] = dfs1["Community Use"].append(dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"].isin(['Outdoor Recreation Facility (Zoo, Golf Course)', 'Observation Tower/Wheel', 'Indoor Recreation Facility'])]).drop(columns =["Theme"])
dfs1["Community Use"].loc[dfs1["Community Use"]["Sub Theme"] == "Outdoor Recreation Facility (Zoo, Golf Course)", "Sub Theme"] = "Outdoor Recreation Facility"
dfs1["Community Use"]["Categories"] = [["Tourist places of interest", "Parks"] if "park" in i.lower() else ["Tourist places of interest", "Library"] if "library" in i.lower() else ["Tourist places of interest"] for i in dfs1["Community Use"]["Place Name"]]
dfs1["Community Use"]["Sub Theme"] = [[i] for i in dfs1["Community Use"]["Sub Theme"]]
dfs1["Community Use"]["Categories"] = dfs1["Community Use"]["Categories"] + dfs1["Community Use"]["Sub Theme"]
dfs1["Community Use"].drop(columns = ["Sub Theme"], inplace=True)

# join the 2 dataframes
df_tourist = dfs["Historic"].append(dfs1["Community Use"])

# add to categories
cat_list = ["Library", "Park", "Zoo", "Museum", "Beach", "Port", "Theatre"]

for i in range(len(df_tourist)):
    for j in cat_list:
        if j in df_tourist["Place Name"].iloc[i]:
            df_tourist["Categories"].iloc[i] = list(set(df_tourist["Categories"].iloc[i] + [j]))
            
            
# drop duplicates and write to file
df_tourist.drop_duplicates(subset = "Place Name", inplace=True)
df_tourist.to_csv("../Data/Output files/Tourist.csv", index = False)

# ------------------------------------------------------------------------------------------- NATURE --------------------------------------------------------------------------------------------------

# join data from vic data tool and melbourne data and format
dfs["PARKS"] = dfs["PARKS"].append(dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"] == 'Informal Outdoor Facility (Park/Garden/Reserve)'].drop(columns=["Theme","Sub Theme"]))
dfs["PARKS"]["Feature Type"] = dfs["PARKS"]["Feature Type"].str.title()
dfs["PARKS"]["Municipality"] = dfs["PARKS"]["Municipality"].str.title()
dfs["PARKS"]["Place Name"] = dfs["PARKS"]["Place Name"].str.title()

# add categories and drop unwanted columns
dfs["PARKS"]["Categories"] = [["Park", "Tourist Place of interest"] if i in ["Botanic Gardens", "National Park"] else ["Park"] for i in dfs["PARKS"]["Feature Type"]]
dfs["PARKS"].drop(columns = ["Feature Type"], inplace = True)

# drop duplicates
dfs["PARKS"].drop_duplicates(subset = ["Place Name"], inplace = True)

# write to file
dfs["PARKS"].to_csv("../Data/Output files/Nature.csv", index=False)
# ------------------------------------------------------------------------------------------- LIBRARY --------------------------------------------------------------------------------------------------


# Create category for library and rename columns 
df_lib["Categories"] = [["Library"] for i in df_lib["LAT"]]
df_lib.rename(columns={"LAT":"Latitude", "LONG": "Longitude"}, inplace=True)

# write to file
df_lib.to_csv("../Data/Output files/Library.csv", index = False)

# ------------------------------------------------------------------------------------------- WORSHIP --------------------------------------------------------------------------------------------------

# Category for place of worship - melbourne data
dfs1["Place of Worship"]["Categories"] = [[i,"Tourist places of interest", "Christian"] if i == "Church" else [i,"Tourist places of interest", "Jew"] if i =="Synagogue" else [i,"Tourist places of interest", "Muslim"] if i == "Mosque" else [i,"Tourist places of interest", "Hindu"] if i == "Mondir" else [i,"Tourist places of interest"] for i in dfs1["Place of Worship"]["Sub Theme"]]
dfs1["Place of Worship"].drop(columns = ["Theme", "Sub Theme"], inplace = True)

# parish data from vic data tool - add categories, format and drop unwanted columns
dfs["PARISH"]["Categories"] = [["Place of Worship", "Parish", "Christianity"] for i in dfs["PARISH"]["Place Name"]]
dfs["PARISH"]["Municipality"] = dfs["PARISH"]["Municipality"].str.title()
dfs["PARISH"]["Place Name"] = dfs["PARISH"]["Place Name"].str.title()
dfs["PARISH"]["Place Name"] = [i+" Parish" for i in dfs["PARISH"]["Place Name"]]
dfs["PARISH"].drop(columns=["Feature Type"], inplace=True)

# join the 2 data
worship = dfs["PARISH"].append(dfs1["Place of Worship"])

# drop duplicates and write to file
worship.drop_duplicates(subset=["Place Name"], keep='first', inplace=True)
worship.to_csv("../Data/Output files/Worship.csv", index = False)
