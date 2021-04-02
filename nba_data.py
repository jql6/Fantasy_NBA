# Functions for transferring data from csvs/dataframes into sql tables
from datetime import date
import json
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelogs, commonallplayers
import pandas as pd
from pathlib import Path
import requests

def get_nba_schedule_json(year, save_flag = False):
    """
        Function that returns a Python dictionary from NBA's game schedule json
        file. Users can also save the file.

        Arguments:  
        year | str (string)  
        The starting year of the season for the schedule you want. For example,
        "2020" would refer to the 2020-2021 season.

        Optional Arguments:  
        save_flag | bool (boolean)  
        Set this to true if you want to save the json file to the current
        directory. The saved file will be called "nba_schedule_" + year + "
        json".

        Returns:  
        A dictionary of NBA's game schedule for the selected year.

        Notes:  
            I think 2015 is the earliest year that can be selected.

            If you're learning the structure of the json file for the first
            time, try saving the file and then opening it in your browser. From
            there you'll be able to explore the structure.

            The acronyms in the json file are explained here by rlabausa:
            https://github.com/rlabausa/nba-schedule-data
    """
    url_part_1 = "http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/"
    url_part_2 = "/league/00_full_schedule.json"
    nba_schedule = requests.get(url_part_1 + year + url_part_2)
    nba_schedule_json = nba_schedule.json()
    
    if save_flag == True:
        # Save the json as a file
        with open("nba_schedule_" + year + ".json", "w") as f:
            json.dump(nba_schedule_json, f)
            
    return nba_schedule_json

def convert_nba_schedule_json_to_df(nba_schedule_json,
                                    csv_file_name = None):
    """
        Function that converts the nba (json file/python dictionary) into a
        single dataframe.

        Arguments:
        nba_schedule_json | dict
        The NBA schedule json file that was pulled from the
        `get_nba_schedule_json` function
        
        Optional arguments:
        csv_file_name | str
        String containing the file name that you want. The '.csv' extension
        is added automatically.

        Returns:
        A dataframe of the data from the nba_schedule_json variable.

        Notes:
            The columns of the returned dataframe are:
                gid = game id
                gdte = game date
                stt = game status
                month = month
                home_team = The abbreviattion of the home team
                home_team_long = The full name of the home team
                away_team = The abbreviation of the away team
                away_team_long = The full name of the away team
    """
    # Intialize a list to store dataframes
    schedules_df_list = []
    # We are iterating through the dictionaries for each month
    for month_i in nba_schedule_json["lscd"]:
        # Get the game jsons/dictionaries for each month
        schedule_df = pd.DataFrame.from_dict(month_i["mscd"]["g"])
        # Filter to selected columns
        selected_cols = ["gid", "gdte", "stt", "h", "v"]
        schedule_df = schedule_df[selected_cols]
        # Extract team names into columns
        schedule_df = schedule_df.assign(
            month = nba_schedule_json["lscd"][0]["mscd"]["mon"],
            home_team = [home_dict.get('ta')
                         for home_dict in schedule_df["h"] if home_dict],
            home_team_long = [home_dict.get('tc') + " " + home_dict.get('tn')
                              for home_dict in schedule_df["h"] if home_dict],
            away_team = [away_dict.get('ta')
                         for away_dict in schedule_df["v"] if away_dict],
            away_team_long = [away_dict.get('tc') + " " + away_dict.get('tn')
                              for away_dict in schedule_df["v"] if away_dict]
        )
        # Remove the home and away dictionaries
        schedule_df.drop("h", axis = 1, inplace = True)
        # `axis = 1` means columns
        # `inplace = True` saves changes
        schedule_df.drop("v", axis = 1, inplace = True)
        # Add the cleaned dataframe to the schedules list
        schedules_df_list.append(schedule_df)
        
    cleaned_schedule_df = pd.concat(schedules_df_list)
    # Replace LA Clippers with Los Angeles Clippers to match Yahoo API
    cleaned_schedule_df.loc[
        cleaned_schedule_df["home_team_long"] == "LA Clippers",
        'home_team_long'
        ] = "Los Angeles Clippers"
    cleaned_schedule_df.loc[
        cleaned_schedule_df["away_team_long"] == "LA Clippers",
        'away_team_long'
        ] = "Los Angeles Clippers"
    
    # Drop the month column
    cleaned_schedule_df = cleaned_schedule_df.drop(['month'], axis = 1)
    
    # Convert the "gdte" column to date
    cleaned_schedule_df["gdte"] = pd.to_datetime(
        cleaned_schedule_df["gdte"]
        )
    
    # Save the data frame to a csv if a file name exists
    if csv_file_name != None:
        # Save to current directory
        csv_path = Path("./data/" + csv_file_name + ".csv")
        cleaned_schedule_df.to_csv(path_or_buf = csv_path,
                                   index = False,
                                   na_rep = 'NULL')

    # Concatenate the list into a large df
    return cleaned_schedule_df

def convert_season_start_to_season_years(starting_year):
    season_year_1 = starting_year
    # Add one to the starting season year, and take the last 2 numbers in the
    # year
    season_year_2 = str(int(season_year_1) + 1)[-2:]
    season_year_full = str(season_year_1) + "-" + str(season_year_2)
    return season_year_full

def get_player_stats(season_start_year, csv_file_name = None):
    """
        Function that gets a dataframe of all player stats for the given
        season. You use this function when you want to download all player data
        instead of just updating recent games.
        
        Arguments:  
        season_start_year | str (string)  
        The starting year of the season for the schedule you want. For example,
        "2020" would refer to the 2020-2021 season.

        Optional arguments:  
        csv_file_name | str  
        String containing the file name that you want. The '.csv' extension
        is added automatically.

        Returns:  
        A dataframe containing the stats for every player for the entire season.
    """
    season_year_full = convert_season_start_to_season_years(
        starting_year = season_start_year
    )
    
    players_df = playergamelogs.PlayerGameLogs(
        season_nullable = season_year_full
    ).player_game_logs.get_data_frame()
    
    # Keep the relevant columns
    players_df = players_df[[
        "SEASON_YEAR", "PLAYER_ID", "PLAYER_NAME", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN",
        "FGM", "FGA", "FTM", "FTA", "FG3M", "PTS", "REB",
        "AST", "STL", "BLK", "TOV"]]
    
    # Convert GAME_DATE to datetime
    players_df["GAME_DATE"] = pd.to_datetime(
        players_df["GAME_DATE"]
    )
    
    # Save the data frame to a csv if a file name exists
    if csv_file_name != None:
        # Save to current directory
        csv_path = Path("./data/" + csv_file_name + ".csv")
        players_df.to_csv(path_or_buf = csv_path,
                          index = False,
                          na_rep = 'NULL')
        
    return players_df
        
def update_player_stats(season_start_year, csv_file_name = None,
                        single_date = None):
    """
    Should save file name as something different from the player df; this
    csv is used to update the table instead of downloading with recent data
    instead of downloading the entire thing again.
    """
    
    if single_date == None:
        single_date = date.today().strftime("%m/%d/%Y")
        
    season_year_full = convert_season_start_to_season_years(
        starting_year = season_start_year
    )
    
    updates_df = playergamelogs.PlayerGameLogs(
        season_nullable = season_year_full,
        date_from_nullable = single_date,
        date_to_nullable = single_date
    ).player_game_logs.get_data_frame()
    
    # Keep the relevant columns
    updates_df = updates_df[[
        "SEASON_YEAR", "PLAYER_ID", "PLAYER_NAME", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN",
        "FGM", "FGA", "FTM", "FTA", "FG3M", "PTS", "REB",
        "AST", "STL", "BLK", "TOV"]]
    
    # Save the data frame to a csv if a file name exists
    if csv_file_name != None:
        # Save to current directory
        csv_path = Path("./data/" + csv_file_name + ".csv")
        updates_df.to_csv(path_or_buf = csv_path,
                          index = False,
                          na_rep = 'NULL')
        
    return updates_df