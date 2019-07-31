
"""
Created by Ross B on 7/25/2019

Scrapes trackman daily status page and returns all tables in a packaged zip file as csvs
"""
import numpy as np
import pandas as pd
import zipfile
from bs4 import BeautifulSoup as bs
from splinter import Browser
from pyvirtualdisplay import Display
import io

def GetTrackmanLogs():

    with Display():
        # Create Browser
        browser = Browser('chrome')

        # Login
        log_url = 'https://trackman.zendesk.com/auth/v2/login/signin'
        browser.visit(log_url)
        browser.find_by_id('user_email').first.fill('rbechtel@texasrangers.com')
        browser.find_by_id('user_password').first.fill('rangers')
        browser.find_by_name('commit').first.click()

        # Get main dfs
        browser.visit('https://trackman.zendesk.com/hc/en-us/articles/360019621773-Daily-Status-Summary#')
        html = browser.html
        dfs = pd.read_html(html)
        main_dfs = []

        # Make top row header
        for df in dfs:
            headers = df.iloc[0]
            main_dfs.append(pd.DataFrame(df.values[1:], columns=headers))

        # Defining key to name csvs appropriately
        main_key = {0:'Missing_List', 1:'Games_in_Limbo', 2:'Re-Delivered_Games', 3:'Recovered_Game_Delivery', 4:'Graveyard', 5:'DND_List', 6:'Reprocessing_Jobs'}

        # Get historical recovered and redelivered
        browser.visit("https://trackman.zendesk.com/hc/en-us/articles/360019753393-Historical-Recovered-and-Re-Delivered-Games")
        html = browser.html
        hrr_dfs = pd.read_html(html)
        hrr_dfs_lst =[]

        # Trackman has blank rows for this table so remove them for sake of cleanliness
        for i in range(len(hrr_dfs)):
            if i != 1:
                hrr_dfs_lst.append(hrr_dfs[i])
            else:
                hrr_dfs_lst.append(hrr_dfs[1].dropna(how = 'all'))

        # Defining key to name csvs appropriately
        hrr_key = {0:'HRR_Re-Delivered_Game_List', 1:'HRR_Recovered_Game_List', 2:'HRR_Recovered_Game_Delivery'}

        # Get graveyard dfs
        browser.visit('https://trackman.zendesk.com/hc/en-us/articles/360019753533-Historical-Graveyard')
        html = browser.html
        g_dfs = pd.read_html(html)
        g_dfs_lst = []

        # Separating for concatination
        headers = ['Game Date', 'Organization', 'Home Team', 'Level', 'Reason']
        head_df = pd.DataFrame(g_dfs[0].values, columns=headers)
        second_df = pd.DataFrame(g_dfs[1].values, columns=headers)
        third_df = pd.DataFrame(g_dfs[2].values, columns=headers)
        third_df

        # Defining key to name csvs appropriately
        g_key = {0:'Historical_Graveyard'}
        g_dfs_lst.append(pd.concat([head_df,second_df,third_df]))

        # Get Historical Calibrations df
        browser.visit('https://trackman.zendesk.com/hc/en-us/articles/360020172133-Historical-Calibrations')
        html = browser.html
        hc_df = pd.read_html(html)[0]

        # Add in empty column that second part has
        city_loc = [np.nan for i in range(len(hc_df))]
        hc_df['City Location'] = city_loc

        # Reorder columns
        hc_df = hc_df[['Date','Location','City Location', 'Organization', 'Home Team', 'Level']]

        # Second part of df is in a list so get list
        soup = bs(html, 'lxml')
        rows = soup.find_all('li')

        # Cleaning text and splitting into columns. Looks hacky but trust me it's legt
        clean_lst = [row.text.replace('\n', '').replace('\xa0','') for row in rows if '-' in row.text and 'Re-Delivered' not in row.text and 'non-networked' not in row.text]
        split_lst = [row.split('-') for row in clean_lst]

        # Defining columns
        date = []
        loc = []
        venue = []

        # Populating columns
        for row in split_lst:
            # Some rows have missing dates
            if len(row) == 2:
                date.append(np.nan)
                loc.append(row[0])
                venue.append(row[1])

            # The '-' in T-Mobile Park messes up the plan
            elif len(row) > 3:
                date.append(row[0])
                loc.append(row[1])
                venue.append(row[2]+ '-' + row[3])

            # Rest are fine
            else:
                date.append(row[0])
                loc.append(row[1])
                venue.append(row[2])

        # Defining empty cols
        org = [np.nan for i in range(len(date))]
        ht = [np.nan for i in range(len(date))]
        lvl = [np.nan for i in range(len(date))]

        # Creating df
        hc_df2 = pd.DataFrame({'Date': date, 'Location': venue, 'City Location': loc, 'Organization': org, 'Home Team': ht, 'Level': lvl})

        # Combine two HC dfs
        hc_key = {0: 'Historical_Calibrations'}
        hc_dfs_lst = []
        hc_dfs_lst.append(pd.concat([hc_df,hc_df2]))

        browser.quit()

    # Convert all
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as csv_zip:
        for i in range(len(main_dfs)):
            csv_zip.writestr(str(main_key[i]) + ".csv", pd.DataFrame(main_dfs[i]).to_csv())
        for i in range(len(hrr_dfs)):
            csv_zip.writestr(str(hrr_key[i]) + ".csv", pd.DataFrame(hrr_dfs_lst[i]).to_csv())
        for i in range(len(g_dfs_lst)):
            csv_zip.writestr(str(g_key[i]) + ".csv", pd.DataFrame(g_dfs_lst[i]).to_csv())
        for i in range(len(hc_dfs_lst)):
            csv_zip.writestr(str(hc_key[i]) + ".csv", pd.DataFrame(hc_dfs_lst[i]).to_csv())

    memory_file.seek(0)
    return memory_file
# End

