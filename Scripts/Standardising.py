#!/usr/bin/env python
# coding: utf-8

# ### import libraries and file

# In[58]:


import pandas as pd
from ast import literal_eval

sub = pd.read_csv("../Data/Suburbs_of_mel.csv")
sports = pd.read_csv("../Data/Output files/Sports.csv")
library = pd.read_csv("../Data/Output files/Library.csv")
tourist = pd.read_csv("../Data/Output files/Tourist.csv")
nature = pd.read_csv("../Data/Output files/Nature.csv")
worship = pd.read_csv("../Data/Output files/Worship.csv")
lga = pd.read_csv("../Data/LGA1.csv")


# In[2]:


sports


# In[3]:


sub


# ### Drop duplicate suburbs

# In[59]:


sub.drop_duplicates(subset=["Locality Name"], inplace = True)


# In[10]:


sub[sub["Locality Name"] == "Carlton North"]


# In[5]:


sub1 = sub[["Municipality Name", "Municipality"]]
sub1.drop_duplicates(inplace = True)


# In[6]:


sports[sports["Municipality"].isna()]


# ### Merge to standardize the municipality name

# In[7]:


sports = pd.merge(sub1,sports, left_on = "Municipality", right_on = "Municipality")


# In[8]:


sports


# In[9]:


sports.columns


# ### Change the municipality and categories column to fit the standard

# In[10]:


sports.drop(columns = ["Municipality"], inplace = True)
sports.rename(columns = {"Municipality Name":"Municipality"}, inplace = True)
sports.reset_index(inplace=True, drop = True)
for i in range(len(sports)):
    if sports.loc[i,"Categories"] != "Martial Arts":
        sports["Categories"][i] = literal_eval(sports["Categories"][i])
        sports.loc[i,"Categories"][0] = sports.loc[i,"Municipality"]
    else:
        sports["Categories"][i] = [sports["Municipality"][i], sports["Municipality"][i], "Sports", "Martial Arts"]
sports


# In[11]:


sports.iloc[298]


# ### Fix the categories and municipality column for library

# In[13]:


library.rename(columns={"Municipality Name": "Municipality", "Locality Name":"Suburb"}, inplace=True)
library.drop(columns = ["Locality Name"], inplace = True)
library


# In[14]:


nature


# ### Fix the categories and municipality column for nature

# In[15]:


for i in range(len(nature)):
    if "city of " in nature["Municipality"][i].lower():
        nature["Municipality"][i] = nature["Municipality"][i][7:] + " City"
    nature["Municipality"][i] = nature["Municipality"][i]+" Council"
    nature["Categories"][i] = literal_eval(nature["Categories"][i])
    nature.loc[i,"Categories"][0] = nature.loc[i,"Municipality"]


# In[16]:


nature


# ### Fix the categories and municipality column for tourist

# In[17]:


tourist


# In[18]:


for i in range(len(tourist)):
    if "city of " in tourist["Municipality"][i].lower():
        tourist["Municipality"][i] = tourist["Municipality"][i][7:] + " City"
    tourist["Municipality"][i] = tourist["Municipality"][i]+" Council"
    tourist["Categories"][i] = literal_eval(tourist["Categories"][i])
    tourist.loc[i,"Categories"][0] = tourist.loc[i,"Municipality"]


# ### Fix the categories and municipality column for worship

# In[21]:


worship


# In[20]:


for i in range(len(worship)):
    if "city of " in worship["Municipality"][i].lower():
        worship["Municipality"][i] = worship["Municipality"][i][7:] + " City"
    worship["Municipality"][i] = worship["Municipality"][i]+" Council"
    worship["Categories"][i] = literal_eval(worship["Categories"][i])
    worship.loc[i,"Categories"][0] = worship.loc[i,"Municipality"]


# In[36]:


set(nature["Suburb"]).difference(set(sub["Locality Name"]))


# In[22]:


nature[nature["Suburb"] == "Heathcote"]


# In[28]:


library[["Municipality","Suburb"]]


# In[43]:


worship[["Municipality","Suburb"]]


# In[46]:


municipalitiesSubs


# In[48]:


nature["Suburb"] = [i.replace("â\xa0Â\xa0","") for i in nature["Suburb"]]
sports["Suburb"] = [i.replace("â\xa0Â\xa0","") for i in sports["Suburb"]]
library["Suburb"] = [i.replace("â\xa0Â\xa0","") for i in library["Suburb"]]
worship["Suburb"] = [i.replace("â\xa0Â\xa0","") for i in worship["Suburb"]]
tourist["Suburb"] = [i.replace("â\xa0Â\xa0","") for i in tourist["Suburb"]]


# In[60]:


sub.rename(columns = {"Municipality":"LGA", "Municipality Name":"Municipality", "Locality Name": "Suburb"}, inplace = True)


# In[61]:


sub[["Municipality","Suburb"]]


# ### Combine municipalities and suburbs

# In[62]:


municipalitiesSubs = nature[["Municipality","Suburb"]]
municipalitiesSubs = municipalitiesSubs.append(sports[["Municipality","Suburb"]])
municipalitiesSubs = municipalitiesSubs.append(library[["Municipality","Suburb"]])
municipalitiesSubs = municipalitiesSubs.append(worship[["Municipality","Suburb"]])
municipalitiesSubs = municipalitiesSubs.append(tourist[["Municipality","Suburb"]])
municipalitiesSubs = municipalitiesSubs.append(sub[["Municipality","Suburb"]])
municipalitiesSubs.drop_duplicates(inplace = True)


# In[63]:


municipalitiesSubs


# In[46]:


set(set(subs)).difference(sub["Locality Name"])


# In[40]:


set(sub["Locality Name"]).difference(set(subs))


# In[70]:


tourist


# ### Write to csv

# In[71]:


municipalitiesSubs.to_csv("../Data/Suburbs_of_mel1.csv")
sports.to_csv("../Data/Output files/Sports.csv")
tourist.to_csv("../Data/Output files/Tourist.csv")
nature.to_csv("../Data/Output files/Nature.csv")
library.to_csv("../Data/Output files/Library.csv")
worship.to_csv("../Data/Output files/Worship.csv")

