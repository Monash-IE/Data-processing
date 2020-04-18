

# uncomment the following 3 lines to install the packages
# !pip install numpy
# !pip install pandas
# !pip install warnings
# !pip install geocoder
# !pip install nltk
# nltk.download('punkt')
### Import pandas and numpy libraries

import pandas as pd
import numpy as np
import warnings
import geocoder
import nltk

warnings.filterwarnings("ignore")

### Read all the required files into separate Dataframes
df = pd.read_csv("../Data/places.csv", encoding = 'ISO-8859-1')
df_melbourne = pd.read_csv("../Data/Greater melbourne region.csv", encoding = 'ISO-8859-1')
df_sport= pd.read_csv("../Data/SportandRec.csv", encoding =  'ISO-8859-1')
df_mel = pd.read_csv("../Data/places_of_interest.csv")
df_lib = pd.read_csv("../Data/libraries.csv")
suburb = pd.read_csv("../Data/suburbs.csv")


# remove escape characters
df_melbourne["Municipality Names"] = df_melbourne["Municipality Names"].str.replace("\xa0", " ")
df_melbourne["LGA"] = df_melbourne["LGA"].str.replace("\xa0", " ")
df_melbourne["Greater melbourne council"] = df_melbourne["Greater melbourne council"].str.replace("\xa0", " ")
df_melbourne["Greater melbourne  LGA"] = df_melbourne["Greater melbourne  LGA"].str.replace("\xa0", " ")


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

# Create column for municipality
df_mel.reset_index(inplace = True, drop = True)
df_mel["Municipality"] = ""
for i in range(len(df_mel)):
    g = geocoder.osm([df_mel["Latitude"][i],df_mel["Longitude"][i]], method='reverse')
#     print(g.json)
    if g.json is not None:
        df_mel["Municipality"][i] = g.json['raw']["address"]['county']

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
df_sport["SuburbTown"] = df_sport["SuburbTown"].str.title()

df_sport ["Address"] = df_sport["StreetNo"] + " " + df_sport["StreetName"]+ " " + df_sport["StreetType"]+ " " + df_sport["SuburbTown"]+ " " + df_sport["Postcode"] 
df_sport.Address = df_sport.Address.str.strip()
df_sport.drop(columns=["StreetNo", "StreetName", "StreetType", "Postcode"], inplace=True)


# sports from melbourne data
sport = dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"].isin(['Major Sports & Recreation Facility','Private Sports Club/Facility', 'Gymnasium/Health Club'])].rename(columns = {"Sub Theme": "Sports Played", "Place Name": "Facility Name"}).drop(columns=["Theme"])


# sports from vic data tool - formatting
dfs["SPORTS"]["Municipality"] = dfs["SPORTS"]["Municipality"].str.title()
dfs["SPORTS"]["Place Name"] = dfs["SPORTS"]["Place Name"].str.title()
dfs["SPORTS"]["Feature Type"] = dfs["SPORTS"]["Feature Type"].str.title()


# rename columns and drop unwanted columns for all the 3 dataframes
dfs["SPORTS"].rename(columns = {"Feature Type": "Sports Played"}, inplace=True)

df_sport.drop(columns = ["FacilityAge", "FacilityUpgradeAge"], inplace = True)
df_sport.rename(columns={"LGA_x":"Municipality", "FacilityName":"Place Name", "SportsPlayed":"Sports Played", "NumberFieldCourts":"Number of Field Courts", "FieldSurfaceType": "Field Surface Type", "FacilityCondition": "Facility Condition", "SuburbTown": "Suburb"}, inplace = True)

df_sport["Municipality"] = df_sport["Municipality"].str.title()

sport["Categories"] = [["Sport", "Sports Facility"] if i =="Major Sports & Recreation Facility" else ["Sport", "Sports Facility", "Private"] if i =="Private Sports Club/Facility" else ["Sports"] for i in sport["Sports Played"]]


# join all the dataframes together
df_sports = df_sport.append(sport).append(dfs["SPORTS"])
                                
# drop duplicates
df_sports.drop_duplicates(subset = ["Place Name", "Latitude", "Longitude"], inplace = True)

# Create categories : Municipality, suburb, sports, sub category

df_sports.reset_index(inplace=True, drop = True)
drop_list = []
                                
# Extract suburb and address for those that do not have data and if no data is available, add it to drop list. Add the suburb to categories
for i in range(len(df_sports)):
    if (type(df_sports["Address"][i]) is float) | (type(df_sports["Suburb"][i]) is float):
        g = geocoder.osm([df_sports["Latitude"][i], df_sports["Longitude"][i]], method='reverse')
    if (g.json is not None) & (type(df_sports["Address"][i]) is float):
        df_sports["Address"][i] = g.json["address"]
    if (g.json is not None) & (type(df_sports["Suburb"][i]) is float) & ("suburb" in g.json):
        df_sports["Suburb"][i] = g.json["suburb"]
    elif ("suburb" not in g.json):
        drop_list.append(i)

# Drop those that do not have suburb

# Drop na in suburb
df_sports.drop(index = drop_list, inplace = True)

df_sports.dropna(subset = ["Suburb"], inplace = True)


df_sports.reset_index(inplace = True, drop=True)

df_sports["Categories"] = [[df_sports["Municipality"][i], df_sports["Suburb"][i]] for i in range(len(df_sports))]

                           
    
# List of sports type that is required
Sport_categories = ["Netball", "Polo", "Rugby", "Shooting", "Skating", "Soccer", "Softball", "Swimming", "Softball", "Table-Tennis", "Tennis", " Volleyball", "Cycling", "Equistrian", "Aerobics", " Archery", "Athletics", "Football", "Badminton", "Baseball", "Basketball", "Boxing", "Cricket", "Gymnasium", "Golf", "Gymnastics", "Hockey", "Canoeing", "Martial-Arts", "Squash", "Motor-Sports", "Sailing", "Wheelchair-Sports", "Croquet", "Lacrosse", "Snooker", "Handball", "Fencing", "Surf", "AFL", "Dancing", "Diving", "Rock-Climbing", "Open-Space", "Skiing", "Boating", "Racecourse", "Playground", "Campground", "Park"]
                                
# drop na values and reset index
df_sports.dropna(subset = ["Sports Played"],  inplace = True)
df_sports.reset_index(inplace = True, drop=True)

to_replace = ["Camp Ground","Table Tennis", "Rock Climbing", "Open Space", "Wheelchair Sports", "Martial Arts", "Motor Sports"]
martial_arts = ["Karate", "Judo", "Tae Kwon Do"]

# Add sports and type of sports to the categories
for i in range(len(df_sports)):
    
    df_sports["Categories"][i].append("Sports")
    if df_sports["Sports Played"][i] in to_replace:
        df_sports["Categories"][i].append(df_sports["Sports Played"][i])
        continue
        
    elif df_sports["Sports Played"][i] in martial_arts:
        df_sports["Categories"][i] = "Martial Arts"
        continue
        
    elif df_sports["Sports Played"][i] == "Gymnasium/Health Club":
        df_sports["Sports Played"][i] = "Gymnasium / Health Club"
        
    else:
        j = nltk.word_tokenize(df_sports["Sports Played"][i])
        cat = set(j).intersection(set(Sport_categories))
        if (bool(cat)):
            df_sports["Categories"][i].append(list(cat)[0])

                               

# write to file
df_sports.to_csv("../Data/Output files/Sports.csv", index = False)



# ------------------------------------------------------------------------------------------- TOURIST --------------------------------------------------------------------------------------------------

# data from vic data tool - formatting
dfs["Historic"]["Feature Type"] = dfs["Historic"]["Feature Type"].str.title()
dfs["Historic"]["Municipality"] = dfs["Historic"]["Municipality"].str.title()
dfs["Historic"]["Place Name"] = dfs["Historic"]["Place Name"].str.title()

# data from melbourne, join similar types, add categories and format
dfs1["Community Use"] = dfs1["Community Use"].append(dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"].isin(['Outdoor Recreation Facility (Zoo, Golf Course)', 'Observation Tower/Wheel', 'Indoor Recreation Facility'])]).drop(columns =["Theme"])
                                    
dfs1["Community Use"].loc[dfs1["Community Use"]["Sub Theme"] == "Outdoor Recreation Facility (Zoo, Golf Course)", "Sub Theme"] = "Outdoor Recreation Facility"
dfs1["Community Use"].rename(columns = {"Sub Theme" : "Feature Type"}, inplace=True)
                                    
dfs1["Community Use"].reset_index(inplace = True, drop = True)

                                 
#  join the 2 dataframes
df_tourist = dfs["Historic"].append(dfs1["Community Use"])

# add to categories municipality, suburb, tourist, type
df_tourist["Suburb"] = np.nan

df_tourist.reset_index(inplace=True, drop = True)

for i in range(len(df_tourist)):
    
    g = geocoder.osm([df_tourist["Latitude"][i], df_tourist["Longitude"][i]], method='reverse')
#     print(g.json)

    
    if (g.json is not None) & ("suburb" in g.json):
        df_tourist["Suburb"][i] = g.json["suburb"]
#         df_tourist["Categories"][i].append(g.json["suburb"])

df_tourist.dropna(subset = ["Suburb"], inplace = True)

df_tourist.reset_index(inplace = True, drop=True)

df_tourist["Categories"] = [[df_tourist["Municipality"][i], df_tourist["Suburb"][i]] for i in range(len(df_tourist))]


cat_list = ["Library", "Park", "Zoo", "Museum", "Beach", "Port", "Theatre"]

for i in range(len(df_tourist)):
    df_tourist["Categories"][i] = df_tourist["Categories"][i] + ["Tourist",df_tourist["Feature Type"][i]]
    
    for j in cat_list:
        if j in df_tourist["Place Name"].iloc[i]:
            df_tourist["Categories"].iloc[i] = df_tourist["Categories"].iloc[i] +list(set([j]))            
            
# drop duplicates and write to file
df_tourist.drop_duplicates(subset = "Place Name", inplace=True)
df_tourist.to_csv("../Data/Output files/Tourist.csv", index = False)

df_tourist

# ------------------------------------------------------- NATURE --------------------------------------------------------------

# join data from vic data tool and melbourne data and format
parks = dfs1["Leisure/Recreation"][dfs1["Leisure/Recreation"]["Sub Theme"] == 'Informal Outdoor Facility (Park/Garden/Reserve)'].drop(columns=["Theme"])
parks.rename(columns = {"Sub Theme": "Feature Type"}, inplace = True)
dfs["PARKS"] = dfs["PARKS"].append(parks)


dfs["PARKS"]["Feature Type"] = dfs["PARKS"]["Feature Type"].str.title()
dfs["PARKS"]["Municipality"] = dfs["PARKS"]["Municipality"].str.title()
dfs["PARKS"]["Place Name"] = dfs["PARKS"]["Place Name"].str.title()

                                
# drop duplicates
dfs["PARKS"].drop_duplicates(subset = ["Place Name"], inplace = True)
dfs["PARKS"].drop_duplicates(subset = ["Latitude", "Longitude"], inplace = True)
                                
# Add categories: Municipality, Suburbs, Category, sub-category
dfs["PARKS"]["Suburb"] = np.nan
dfs["PARKS"].reset_index(inplace=True, drop = True)

for i in range(len(dfs["PARKS"])):
    
    g = geocoder.osm([dfs["PARKS"]["Latitude"][i], dfs["PARKS"]["Longitude"][i]], method='reverse')
#     print(g.json)

    
    if (g.json is not None) & ("suburb" in g.json):
        dfs["PARKS"]["Suburb"][i] = g.json["suburb"]

dfs["PARKS"].dropna(subset = ["Suburb"], inplace = True)

dfs["PARKS"].reset_index(inplace = True, drop = True)

dfs["PARKS"]["Categories"] = [[dfs["PARKS"]["Municipality"][i], dfs["PARKS"]["Suburb"][i]] for i in range(len(dfs["PARKS"]))]

                               
dfs["PARKS"]["Categories"] = [dfs["PARKS"]["Categories"][i] + ["Tourist", "Park"] if dfs["PARKS"]["Feature Type"][i] in ["Botanic Gardens", "National Park"] else dfs["PARKS"]["Categories"][i] + ["Park"] for i in range(len(dfs["PARKS"]))]

                  
# write to file
dfs["PARKS"].to_csv("../Data/Output files/Nature.csv", index=False)

# ----------------------------------------------------------- LIBRARY -------------------------------------------------------------------


# Create category for library and rename columns 
df_lib["Categories"] = [[df_lib["Municipality Name"][i],df_lib["Suburb/Town"][i],"Library"] for i in range(len(df_lib))]
df_lib.rename(columns={"LAT":"Latitude", "LONG": "Longitude", "Suburb/Town" : "Suburb"}, inplace=True)

# write to file
df_lib.to_csv("../Data/Output files/Library.csv", index = False)

# ------------------------------------------------------------------------------------------- WORSHIP --------------------------------------------------------------------------------------------------

dfs1["Place of Worship"].drop(columns = ["Theme", "Sub Theme"], inplace = True)

# parish data from vic data tool - format and drop unwanted columns
dfs["PARISH"]["Municipality"] = dfs["PARISH"]["Municipality"].str.title()
dfs["PARISH"]["Place Name"] = dfs["PARISH"]["Place Name"].str.title()
dfs["PARISH"]["Place Name"] = [i+" Parish" for i in dfs["PARISH"]["Place Name"]]
dfs["PARISH"].drop(columns=["Feature Type"], inplace=True)

# join the 2 data and drop duplicates
worship = dfs["PARISH"].append(dfs1["Place of Worship"])
worship.drop_duplicates(subset=["Place Name"], keep='first', inplace=True)

# Add categories municipalit, suburb, worship, type
worship["Suburb"] = np.nan
worship.reset_index(inplace=True, drop = True)

for i in range(len(worship)):
    
    g = geocoder.osm([worship["Latitude"][i], worship["Longitude"][i]], method='reverse')
#     print(g.json)

    
    if (g.json is not None) & ("suburb" in g.json):
        worship["Suburb"][i] = g.json["suburb"]

worship.dropna(subset = ["Suburb"], inplace = True)

worship.reset_index(inplace = True, drop = True)
       
worship["Categories"] = [[worship["Municipality"][i], worship["Suburb"][i]] for i in range(len(worship))]



for i in range(len(worship)):
    worship["Categories"][i].append("Worship")
    
    if "Parish" in worship["Place Name"][i]:
        worship["Categories"][i] = worship["Categories"][i] + ["Parish", "Christian"]
        
    if ("Church" in worship["Place Name"][i]) | ("Cathedral" in worship["Place Name"][i]):
        worship["Categories"][i] = worship["Categories"][i] + ["Church", "Christian"]
    
    if "Mosque" in worship["Place Name"][i]:
        worship["Categories"][i] = worship["Categories"][i] + ["Mosque", "Muslim"]
        
    if "Synagogue" in worship["Place Name"][i]:
        worship["Categories"][i] = worship["Categories"][i] + ["Synagogue", "Jew"]
        
    if "Mondir" in worship["Place Name"][i]:
        worship["Categories"][i] = worship["Categories"][i] + ["Mondir", "Hindu"]
        
    if "Temple" in worship["Place Name"][i]:
        worship["Categories"][i] = worship["Categories"][i] + ["Temple", "Hindu"]
    
    

# write to file
worship.to_csv("../Data/Output files/Worship.csv", index = False)

