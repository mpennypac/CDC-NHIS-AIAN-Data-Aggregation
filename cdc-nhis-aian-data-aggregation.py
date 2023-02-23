import pandas as pd
import numpy as np
from Levenshtein import distance
from Levenshtein import ratio
import tabula as tb
import re

"""## pdf conversion 2019-onwards
data = tb.read_pdf('adult-summary-2020.pdf', pages=str('25'), area=(40, 70, 600, 650),
                   pandas_options={'header': None}, lattice=True)[0]
print(data[[2, 4]].dropna())"""
"""df = pd.DataFrame()
count = 1
top = 100
for page_num in range(28):
    if count > 1:
        top = 40
    data = tb.read_pdf('adult-summary-2020.pdf',pages=str(page_num+1),area=(top,70,600,650),pandas_options={'header':None},lattice=True)[0]
    for row in range(len(data)):
        for element in data.iloc[row]:
            #print(element)
            if element == 'Variable Name':
                varname = data.iloc[row][data.iloc[row] == 'Variable Name'].index[0]
            elif element == 'Description':
                description = data.iloc[row][data.iloc[row] == 'Description'].index[0]
    data = data[[varname, description]]
    data = data.rename(columns={varname:'Variable Name',description:'Description'})
    data = data[(data['Variable Name'] != 'Variable Name')]
    data = data.dropna()
    print(data)
    print()
    df = pd.concat([df, data]).reset_index(drop=True)
    count += 1
    print(df)
    print('---------------')

df.to_csv('adult-summary-2020.csv')"""


"""## pdf conversion 2014-2018
df = pd.DataFrame()
count = 1
for page_num in range(28):
    data = tb.read_pdf('adult-summary-2015.pdf', pages=str(page_num + 1), area=(110,0,1000,800),pandas_options={'header': None},stream=True)[0]
    varname = data.iloc[0][data.iloc[0] == 'FinalDocName'].index[0]
    description = data.iloc[0][data.iloc[0] == 'Processing Variable Label'].index[0]
    data = data[[varname, description]]
    data = data.rename(columns={varname:'Variable Name',description:'Description'})
    data = data.dropna()
    df = pd.concat([df, data]).reset_index(drop=True)
    if count > 1:
        df = df[(df['Variable Name'] != 'FinalDocName')]
    count += 1
    print(df)
    print('-----------')

#print(df[(df['Variable Name' != 'FinalDocName'])])
df.to_csv('adult-summary-2015.csv')"""


df2021 = pd.read_csv('adult21.csv')
df2021 = df2021.loc[df2021['RACEALLP_A'] == 4]

df2020 = pd.read_csv('adult20.csv')
df2020 = df2020.loc[df2020['RACEALLP_A'] == 4]

df2019 = pd.read_csv('adult19.csv')
df2019 = df2019.loc[df2019['RACEALLP_A'] == 4]

df2018 = pd.read_csv('adult18.csv')
df2018 = df2018.loc[df2018['RACERPI2'] == 3]

df2017 = pd.read_csv('adult17.csv')
df2017 = df2017.loc[df2017['RACERPI2'] == 3]

df2016 = pd.read_csv('adult16.csv')
df2016 = df2016.loc[df2016['RACERPI2'] == 3]

df2015 = pd.read_csv('adult15.csv')
df2015 = df2015.loc[df2015['RACERPI2'] == 3]


dataframes = {'2021':df2021,
              '2020':df2020,
              '2019':df2019,
              '2018':df2018,
              '2017':df2017,
              '2016':df2016,
              '2015':df2015}


master_data = pd.DataFrame()
var_changes = pd.DataFrame()
master_desc = pd.DataFrame()

count = 1

for df_name in dataframes.keys():
    df = dataframes[df_name]
    df_na = list(df[df.columns[df.isna().all()]].columns)
    df = df.drop(df_na,axis=1)
    df['year'] = int(df_name)

    df_desc = pd.read_csv('adult-summary-{0}.csv'.format(df_name))

    if count == 1:
        master_data = pd.concat([master_data, df]).reset_index(drop=True)
        master_desc = df_desc[~df_desc['Variable Name'].isin(df_na)].reset_index(drop=True)
    elif count > 1:
        master_only_vars = np.setdiff1d(master_data.columns, df.columns)
        df_only_vars = np.setdiff1d(df.columns, master_data.columns)

        for df_var in df_only_vars:
            df_var_desc = df_desc.loc[df_desc[df_desc['Variable Name'] == df_var].index[0], 'Description']
            for master_var in master_only_vars:
                master_var_desc = master_desc.loc[master_desc[master_desc['Variable Name'] == master_var].index[0], 'Description']
                print('comparing', df_var, 'and', master_var, '...')
                print(df_var_desc)
                print(master_var_desc)

                if distance(df_var, master_var) == 1:
                    print('near match variable name found')
                    df = df.rename(columns={df_var:master_var})
                    master_desc.loc[master_desc[master_desc['Variable Name'] == master_var].index[0], '{0} Edit'.format(df_name)] = df_var_desc
                    var_changes.loc[count, 'Year of Edit'] = df_name
                    var_changes.loc[count, 'New Var Name'] = master_var
                    var_changes.loc[count, 'Old Var Name'] = df_var
                    var_changes.loc[count, 'Old Var Desc'] = df_var_desc
                elif distance(df_var, master_var) > 1 and ratio(df_var_desc, master_var_desc) >= 0.95:
                    print('near match variable description found')
                    df = df.rename(columns={df_var: master_var})
                    master_desc.loc[master_desc[master_desc['Variable Name'] == master_var].index[0], '{0} Edit'.format(df_name)] = df_var_desc
                    var_changes.loc[count, 'Year of Edit'] = df_name
                    var_changes.loc[count, 'New Var Name'] = master_var
                    var_changes.loc[count, 'Old Var Name'] = df_var
                    var_changes.loc[count, 'Old Var Desc'] = df_var_desc
                print('----')

        common_vars = np.intersect1d(df.columns, master_data.columns)
        #print(master_data[common_vars])
        #print(df[common_vars])
        master_data = pd.concat([master_data[common_vars].reset_index(drop=True), df[common_vars].reset_index(drop=True)], axis=0).reset_index(drop=True)
        master_desc = master_desc[master_desc['Variable Name'].isin(common_vars)].reset_index(drop=True)

    #most_recent_year = df_name


    print(master_data)
    print()
    print(master_desc)
    print('-------------------------------')
    count += 1

master_data.to_csv('master-data.csv')
master_desc.to_csv('master-desc.csv')
var_changes.to_csv('var-change-log.csv')