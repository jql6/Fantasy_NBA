"""
Python script for scraping NBA and Yahoo Fantasy Sports data into a PostgreSQL
database.

Title: NBA and Yahoo Fantasy Sports data scraper
Author: Jackie Lu
Date: 2021, Mar. 23

Instructions:
Edit the private.json and sql_login.json fields to your emails/passwords.
The program assumes that you have the json file in the same directory
as where you're running this python file.
"""

# Libraries
import json
import pandas as pd
from pathlib import Path
import psycopg2
import re
import webbrowser

from yahoo_oauth import OAuth2

# My functions
import df_to_sql # df_to_sql.py file
import nba_data # nba_data.py file

# Disable yahoo_oauth logging
import logging
oauth_logger = logging.getLogger('yahoo_oauth')
oauth_logger.disabled = True

# Function that takes a data frame and outputs a psycopg2 cursor.execute
# command that creates the table for it

# YahooData class
class YahooData:
    """
        Class with methods that get data from Yahoo's API.
        
        Attributes:  
        private_json_path | str  
        This is the path to your `private.json` file. See __init__ for details
        on what your `private.json` file should look like.
        
        league_id | str  
        A string containing your league id. To find your league id,
        go to https://basketball.fantasysports.yahoo.com/nba
        then click League -> Settings and you'll see the League ID
        displayed there.
        
        oauth | yahoo_oauth.oauth.OAuth2 object  
        Acts as a 'key' for accessing you Yahoo Fantasy Sports data. Obtained
        from the refresh_oauth method.
        
        game_key | str  
        String containing your game key. Obtained from the get_game_key method.
    """
    def __init__(self, your_league_id,
                 path_to_private_json = "./private.json"):
        """
            Arguments:  
            your_league_id | str  
            A string containing your league id. To find your league id,
            go to https://basketball.fantasysports.yahoo.com/nba
            then click League -> Settings and you'll see the League ID
            displayed there.
            
            Optional Arguments:  
            path_to_private_json | str  
            The path to your `private.json` file. This file should contain your
            consumer key and consumer secret. It should look like this:
            ```
            {
              "consumer_key": "ENTER_CONSUMER_KEY_STRING",
              "consumer_secret": "ENTER_CONSUMER_SECRET_STRING"
            }
            ```
        """
        self.league_id = str(your_league_id)
        self.private_json_path = Path(path_to_private_json)
        self.oauth = None
        self.game_key = None
        self.league_dict = None
        
        if not self.private_json_path.exists():
            print("Warning, '{}' not found!".format(self.private_json_path))
        
    def __repr__(self):
        return (f"YahooData({self.league_id!r}, {self.private_json_path!r})")
    
    def __str__(self):
        return (f"YahooData\nleague id: {self.league_id}\npath to private json path: {self.private_json_path}\n")
        
    def refresh_oauth(self):
        """
            Method that initializes or refreshes the `oauth` attribute.
        """
        self.oauth = OAuth2(consumer_key = None,
                            consumer_secret = None,
                            from_file = self.private_json_path)
    
    
    def get_game_key(self):
        """
            Method that adds the `game_key` attribute.
        """
        yahoo_url = (
            'https://fantasysports.yahooapis.com/fantasy/v2/game/nba'
            )
        # This json contains the game key
        json_response = self.oauth.session.get(
            yahoo_url,params = {"format": "json"}
        ).json()
        # Create the game_key attribute
        self.game_key = json_response["fantasy_content"]\
                ["game"][0]["game_key"]
    
    
    def get_league_info(self):
        """
            Method that gets league_dict.
        """
        yahoo_url = (
            'https://fantasysports.yahooapis.com/fantasy/v2/league/' +
            self.game_key + '.l.' + self.league_id + '/'
            )
        json_response = self.oauth.session.get(
            yahoo_url, params = {"format": "json"}
            ).json()
        
        self.league_dict = json_response["fantasy_content"]["league"][0]
    
    
    def get_yahoo_scoreboard(self, week_number = None):
        """
            Method that gets you a scoreboard json for the given week.
            
            Optional Arguments:
            week_number | str (string)
            The string containing the week number of the scoreboard you want.
            By default, if week_number is None, then it will just take the
            current week.
            
            Returns:
            A dictionary of the week's matchup.
        """
        # By default set week_number to current_week
        if week_number == None:
            week_number = self.league_dict["current_week"]
        # Otherwise check that the provided week is valid
        else:
            start_week = self.league_dict["start_week"]
            end_week = self.league_dict["end_week"]
            # Notify user is week_number is out of range
            assert (int(start_week) <= int(week_number)),\
                    ("week_number: {} must be >= start week: {}."\
                     .format(week_number, start_week))

            assert (int(week_number) <= int(end_week)),\
                    ("week_number: {} must be <= end week: {}."\
                     .format(week_number, end_week))
        
        # Getting the scoreboard
        yahoo_url = (
            'https://fantasysports.yahooapis.com/fantasy/v2/league/' +
            str(self.game_key) + '.l.' + str(self.league_id) + '/' +
            'scoreboard;week=' + str(week_number)
            )
        # This json contains the game key
        json_response = self.oauth.session.get(
            yahoo_url, params = {"format": "json"}
            ).json()
        
        return json_response
    
    # Modify this method so that it saves to the current directory
    # with a file name unless file name is None.
    @staticmethod
    def get_yahoo_matchups(scoreboard_json,
                           csv_file_name = None):
        """
            Function that returns a dataframe of the matchup info of a given
            scoreboard.
            
            Arguments:  
            scoreboard_json | dict  
            Variable that contains the matchup json from `get_yahoo_scoreboard`.
            
            Optional arguments:  
            csv_file_name | str  
            String containing the file name that you want. The '.csv' extension
            is added automatically.
            
            Returns:  
            A data frame containing the matchups from the given json variable.
            Can also save the dataframe to the current directory as a csv.
        """
        scoreboard_info = scoreboard_json["fantasy_content"]["league"]
        current_week = scoreboard_info[0]["current_week"]
        current_season = scoreboard_info[0]["season"]
        scoreboard_data = [d["scoreboard"]
                           for d in scoreboard_info
                           if "scoreboard" in d][0]
        all_matchups = scoreboard_data["0"]["matchups"]
        # Initialize dataframe to hold the matchups
        matchup_info = []
        
        for i in range(all_matchups["count"]):
            # Add the values for a matchup
            # These are the same for any given team
            current_matchup_list = []
            current_matchup_list.append(current_season)

            selected_matchup = all_matchups[str(i)]["matchup"]
            current_matchup_list.append(selected_matchup["week"])
            current_matchup_list.append(selected_matchup["week_start"])
            current_matchup_list.append(selected_matchup["week_end"])
            current_matchup_list.append(i + 1)
            current_matchup_list.append(selected_matchup["status"])
            current_matchup_list.append(
                bool(int(selected_matchup["is_playoffs"]))
                )
            current_matchup_list.append(
                bool(int(selected_matchup["is_consolation"]))
                )

            # These values are different for different teams
            current_matchup = selected_matchup["0"]["teams"]
            for j in range(current_matchup["count"]):
                team_name = [d["name"]
                         for d in current_matchup[str(j)]["team"][0]
                         if "name" in d][0]

                team_key = [d["team_key"]
                            for d in current_matchup[str(j)]["team"][0]
                            if "team_key" in d][0]

                team_stats = current_matchup[str(j)]["team"][1]\
                        ["team_stats"]["stats"]
                FG_string = team_stats[0]["stat"]["value"]
                # Get numbers before the "/"
                FGM = int(re.search("^\d*(?=\/)", string = FG_string).group(0)
                          or 0)
                # Get numbers after the "/"
                FGA = int(re.search("(?<=\/)\d*$", string = FG_string).group(0)
                          or 0)
                FG_PCT = float(team_stats[1]["stat"]["value"]
                               or "NaN")

                FT_string = team_stats[2]["stat"]["value"]
                # Get numbers before the "/"
                FTM = int(re.search("^\d*(?=\/)", string = FT_string).group(0)
                          or 0)
                # Get numbers after the "/"
                FTA = int(re.search("(?<=\/)\d*$", string = FT_string).group(0)
                          or 0)
                FT_PCT = float(team_stats[3]["stat"]["value"]
                               or "NaN")

                FG3M = int(team_stats[4]["stat"]["value"] or 0)
                PTS = int(team_stats[5]["stat"]["value"] or 0)
                REB = int(team_stats[6]["stat"]["value"] or 0)
                AST = int(team_stats[7]["stat"]["value"] or 0)
                STL = int(team_stats[8]["stat"]["value"] or 0)
                BLK = int(team_stats[9]["stat"]["value"] or 0)
                TOV = int(team_stats[10]["stat"]["value"] or 0)
                
                stat_type = "Actual"

                matchup_info.append(current_matchup_list +
                                    [team_name, team_key, FGM, FGA, FG_PCT,
                                     FTM, FTA, FT_PCT, FG3M, PTS, REB, AST,
                                     STL, BLK, TOV, stat_type])

        column_list = ["season", "week", "week_start", "week_end",
                       "matchup_number", "status", "is_playoffs",
                       "is_consolation", "team_name",  "team_key",
                       "FGM", "FGA", "FG_PCT", "FTM", "FTA", "FT_PCT",
                       "FG3M", "PTS", "REB", "AST", "STL", "BLK", "TOV",
                       "stat_type"]
        
        matchup_info_df = pd.DataFrame.from_records(
            matchup_info, columns = column_list
            )
        
        # Convert the date columns from object type to datetime type
        matchup_info_df["week_start"] = pd.to_datetime(
            matchup_info_df["week_start"]
            )
        matchup_info_df["week_end"] = pd.to_datetime(
            matchup_info_df["week_end"]
            )
        
        # Save the data frame to a csv if a file name exists
        if csv_file_name != None:
            # Save to current directory
            csv_path = Path("./data/" + csv_file_name + ".csv")
            matchup_info_df.to_csv(path_or_buf = csv_path,
                                   index = False,
                                   na_rep = 'NULL')
        
        return matchup_info_df
    
    
    def get_yahoo_rosters(self,
                          csv_file_name = None):
        """
            Function that returns the roster for all teams in the fantasy
            league.
    
            Optional arguments:  
            csv_file_name | str  
            string containing the file name that you want. The '.csv' extension
            is added automatically.
    
            Returns:  
            A dataframe containing the rosters for every team.
        """
        # Initialize list for the data frame rows
        roster_list = []
        
        for i in range( self.league_dict["num_teams"] ):
            team_key = self.league_dict["league_key"] + ".t." + str(i + 1)
            # Getting the scoreboard
            yahoo_url = (
                "https://fantasysports.yahooapis.com/fantasy/v2/team/" +
                team_key + "/roster/players"
                )

            # This gets the team roster json file
            team_roster_json = self.oauth.session.get(
                yahoo_url, params = {"format": "json"}
                ).json()

            team_roster = team_roster_json["fantasy_content"]["team"][1]\
                    ["roster"]
            owning_team = team_roster_json["fantasy_content"]["team"][0]\
                    [2]["name"]
            roster_size = team_roster["0"]["players"]["count"]

            for player_num in range(0, int(roster_size)):
                df_row = [owning_team]
                num_string = str(player_num)
                # Full name
                player_dict_list = team_roster["0"]["players"][num_string]\
                        ["player"][0]
                full_name = [d["name"] for d in player_dict_list
                             if "name" in d][0]["full"]
                df_row.append(full_name)

                # Team abbreviation
                team_abbreviation = [d["editorial_team_full_name"]
                                     for d in player_dict_list
                                     if "editorial_team_full_name" in d][0]
                df_row.append(team_abbreviation)

                # List of positions
                all_positions = [d["eligible_positions"] for d in
                                 player_dict_list
                                 if "eligible_positions" in d][0]
                # Available positions
                all_positions = [pos["position"] for pos in all_positions]
                df_row.append(all_positions)

                # Injury status
                try:
                    injury_status = [d["status"] for d in player_dict_list
                                     if "status" in d][0]
                except:
                    injury_status = "NONE"

                df_row.append(injury_status)

                roster_list.append(df_row)

            # https://stackoverflow.com/a/45313942/13303696
            roster_df = pd.DataFrame.from_records(
                roster_list,
                columns = ['owning_team', 'player_name', 'team_name',
                           'positions', 'injury_status']
            )
            # Column that we want to one hot encode
            column_name = "positions"
            
            roster_df = roster_df.drop(column_name, 1).join(
                pd.get_dummies(
                    pd.DataFrame(roster_df[column_name].tolist()).stack()
                ).astype(int).sum(level=0).astype(bool)
            )
            # Change the "IL +" column to "IL plus"
            roster_df.rename(columns = {'IL+':'IL_plus'}, inplace = True)

            # Save the data frame to a csv if a file name exists
            if csv_file_name != None:
                # Save to current directory
                csv_path = Path("./data/" + csv_file_name + ".csv")
                roster_df.to_csv(path_or_buf = csv_path,
                                 index = False,
                                 na_rep = 'NULL')

        return(roster_df)


"""
Custom functions
"""

def refresh_SQL_data(database_connection,
                     yahoo_data_object,
                     refresh_matchups = False,
                     refresh_rosters = False,
                     refresh_schedule = False,
                     initialize_players = False,
                     refresh_players = False):
    """
        Function that refreshes the csv files and imports them into the
        database through the connection given.
        
        Arguments:  
        database_connection | psycopg2.extensions.connection  
        Variable obtained through `psycopg2.connect()`
        
        yahoo_data_object | __main__.YahooData  
        Variable containing Yahoo API data obtained through `YahooData()`.
        It must have the property `league_dict`.
        
        Optional arguments:  
        refresh_matchups | bool  
        Flag indicating whether or not you want to refresh the Yahoo_Matchups
        SQL table.
        
        refresh_rosters | bool  
        Flag indicating whether or not you want to refresh the Yahoo_Rosters
        SQL table.
        
        refresh_schedule | bool  
        Flag indicating whether or not you want to refresh the NBA_Schedule
        SQL table.
        
        initialize_players | bool  
        Flag indicating whether or not you want to download the entire
        NBA_Players data and import it into an SQL table.
        
        refresh_players | bool  
        Flag indicating whether or not you want to refresh the NBA_Players
        SQL table.
        
        Returns:  
        None. Check the SQL database to see if the tables have been updated.
        You can also check the "./data" folder to see if the csv files have
        been updated too.
    """
    # Quick check of the players flags
    if initialize_players == True & refresh_players == True:
        return ("Error, only one of `initialize_players`, or " +
                "`refresh_players` may be `True`!")
    
    # Create scoreboard json
    json1 = yahoo_data_object.get_yahoo_scoreboard()
    
    # Link the relevant data
    refresh_dict = {
        "names": ["Yahoo_Matchups", "Yahoo_Rosters", "NBA_Schedule",
                  "NBA_Players", "temp_NBA_Players"],
        "flags": [bool(refresh_matchups),
                  bool(refresh_rosters),
                  bool(refresh_schedule),
                  bool(initialize_players),
                  bool(refresh_players)]
    }
    refresh_dict["dfs"] = [None] * len(refresh_dict["names"])
    # Initialize a list of sql commands
    sql_commands = []
    
    # Get data frames
    if refresh_dict["flags"][0] == True:
        # Get the scoreboard df
        refresh_dict["dfs"][0] = yahoo_data_object.get_yahoo_matchups(
            scoreboard_json = json1,
            csv_file_name = refresh_dict["names"][0]
        )

        
    if refresh_dict["flags"][1] == True:
        # Get the roster df
        try:
            refresh_dict["dfs"][1] = yahoo_data_object.get_yahoo_rosters(
                csv_file_name = refresh_dict["names"][1]
            )
        except:
            print("Error, yahoo_class could not get Yahoo rosters!")
    
    if refresh_dict["flags"][2] == True:
        # Get the schedule df
        try:
            nba_schedule_json = nba_data.get_nba_schedule_json(
                year = yahoo_data_object.league_dict["season"],
                save_flag = False
            )
            refresh_dict["dfs"][2] = nba_data.convert_nba_schedule_json_to_df(
                nba_schedule_json = nba_schedule_json,
                csv_file_name = refresh_dict["names"][2]
            )
        except:
            print("Error, could not retrieve NBA schedule!")
    
    if refresh_dict["flags"][3] == True:
        # Get the players df
        try:
            refresh_dict["dfs"][3] = nba_data.get_player_stats(
                season_start_year = yahoo_data_object.league_dict["season"],
                csv_file_name = refresh_dict["names"][3]
                )
            print(refresh_dict["dfs"][3].shape)
        except:
            print("Error, could not retrieve NBA players!")
    
    if refresh_dict["flags"][4] == True:
        # Get the players df
        try:
            refresh_dict["dfs"][4] = nba_data.update_player_stats(
                season_start_year = yahoo_data_object.league_dict["season"],
                csv_file_name = refresh_dict["names"][4]
                )
            print(refresh_dict["dfs"][4].shape)
        except:
            print("Error, could not retrieve NBA players today!")

    # Get the sql commands
    for index, flag in enumerate(refresh_dict["flags"]):
        # If the user wants the data refreshed
        if flag == True:
            print(refresh_dict["names"][index])
            # Generate the sql command
            sql_command = df_to_sql.convert_df_to_sql_command(
                table_name = refresh_dict["names"][index],
                df1 = refresh_dict["dfs"][index]
            )
            # Append it to the list of sql commands
            sql_commands.append(sql_command)
            
    # Create database connection cursor
    cursor = database_connection.cursor()
    # Loop through the commands and execute them
    for index in range(0, len(sql_commands)):
        # Create the tables in SQL
        cursor.execute(
            """
            {}
            """.format(sql_commands[index])
        )
    
    # Commit the sql commands
    database_connection.commit()
    cursor.close()
    # Loop through the flags and update values if needed
    for index, flag in enumerate(refresh_dict["flags"]):
        if flag == True:
            # If it's the player update thing
            if refresh_dict["names"][index] == "temp_NBA_Players":
                # Do a different SQL command
                # Drop rows with the given date
                # Add rows with the given date
                print("temp_NBA_players flag activated")
            
            df_to_sql.import_csv_to_sql(
                database_connection = database_connection,
                path_to_csv = ("./data/" + refresh_dict["names"][index] +
                               ".csv"),
                table_name = refresh_dict["names"][index])
    
    cursor = database_connection.cursor()
    # Fix difference between Yahoo API and NBA API
    cursor.execute(
        """
        UPDATE yahoo_rosters
        SET player_name = REPLACE(player_name,
                                  'PJ Washington', 'P.J. Washington')
        """
    )
    cursor.execute(
        """
        UPDATE nba_players
        SET team_name = REPLACE(team_name,
                                'LA Clippers', 'Los Angeles Clippers')
        """
    )
    database_connection.commit()
    cursor.close()
  
"""
The commands
"""


# Open browser for user to the link if user doesn't know league id
know_league_id = input(
    "Optional: Enter `1` if you don't know your league id: \n"
    )

if (know_league_id == "1"):
    webbrowser.open(url = "https://login.yahoo.com/?.lang=en-US&src=fantasy&.done=https%3A%2F%2Fbasketball.fantasysports.yahoo.com%2Fnba&pspid=782202766&activity=ybar-signin")


# Construct the object from the class
yahoo_class = YahooData(your_league_id = "1157") # Add your league id here
# Generate the oauth
yahoo_class.refresh_oauth()
# Show that the oauth is generated
print(yahoo_class.oauth)
# Generate game key
yahoo_class.get_game_key()
# Get the league info for the scoreboard
yahoo_class.get_league_info()

nba_data.get_player_stats(
    season_start_year = yahoo_class.league_dict["season"],
    csv_file_name = "NBA_Players"
    )
nba_data.update_player_stats(
    season_start_year = yahoo_class.league_dict["season"],
    csv_file_name = "temp_NBA_Players"
    )


login_info = json.load(open("./sql_login.json"))

conn = psycopg2.connect(
    host = login_info["host"],
    database = login_info["database"],
    user = login_info["user"],
    password = login_info["password"]
)


refresh_SQL_data(database_connection = conn,
                 yahoo_data_object = yahoo_class,
                 refresh_matchups = True,
                 refresh_rosters = True,
                 refresh_schedule = True,
                 initialize_players = True,
                 refresh_players = False)


###
# Queries
###

cursor = conn.cursor()

# Massive query
query1 = ("""
          /* Function that gets season_year from nba_players */
          DROP TABLE IF EXISTS projections;
          
          DROP FUNCTION IF EXISTS get_season_year();
          CREATE FUNCTION get_season_year() RETURNS text
          AS $$
          #print_strict_params on
          DECLARE
          season_year_text text;
          BEGIN
              SELECT season_year INTO STRICT season_year_text FROM (
          		SELECT season_year, count(season_year) as counter
                FROM nba_players
          		GROUP BY season_year ORDER BY counter DESC
          		LIMIT 1
          	) as season_year_query;
              RETURN season_year_text;
          END;
          $$ LANGUAGE plpgsql;
          
          /* Function that gets starting week from yahoo_matchups */
          DROP FUNCTION IF EXISTS get_week_start();
          CREATE FUNCTION get_week_start() RETURNS date
          AS $$
          #print_strict_params on
          DECLARE
          week_start_date date;
          BEGIN
              SELECT yahoo_matchups.week_start INTO STRICT week_start_date
                  FROM yahoo_matchups LIMIT 1;
              RETURN week_start_date;
          END;
          $$ LANGUAGE plpgsql;
          
          /* Function that gets ending week from yahoo_matchups */
          DROP FUNCTION IF EXISTS get_week_end();
          CREATE FUNCTION get_week_end() RETURNS date
          AS $$
          #print_strict_params on
          DECLARE
          week_end_date date;
          BEGIN
              SELECT yahoo_matchups.week_end INTO STRICT week_end_date
                  FROM yahoo_matchups LIMIT 1;
              RETURN week_end_date;
          END;
          $$ LANGUAGE plpgsql;
          
          /**
           * Actual query
           **/
          
          CREATE TABLE projections AS(
              WITH games_left_t AS(
                  SELECT t1.owning_team, t1.player_name, t1.team_name,
                  t1.injury_status,
          	    CASE /* If player isn't healthy, set games_left to 0 */
          		    WHEN t1.injury_status != 'NONE' THEN 0
          		    ELSE t2.games_left
          		END AS games_left
          	    FROM yahoo_rosters AS t1
          	    INNER JOIN
                  /* Table that calculates games left from schedule by
                 counting the team's name in the home and away columns. */
          	    (SELECT team_name, count(*) AS games_left FROM
          		(SELECT home_team_long AS team_name FROM nba_schedule
                   /* Hard coded */
          		 WHERE (gdte BETWEEN get_week_start() AND get_week_end())
                   AND (stt != 'Final')
          		 UNION ALL
          		 SELECT away_team_long AS team_name FROM nba_schedule
                   /* Hard coded */
          		 WHERE (gdte BETWEEN get_week_start() AND get_week_end())
                   AND (stt != 'Final')) AS myTab1
          	    GROUP BY team_name) AS t2
          	    ON t1.team_name = t2.team_name
              )
          
              SELECT t2.owning_team, t1.season_year, t1.player_name,
                  t2.team_name,
              t2.injury_status, t3.games_left,
              round(AVG(t1.fgm), 2) * t3.games_left AS fgm,
              round(AVG(t1.fga), 2) * t3.games_left AS fga,
              round(AVG(t1.ftm), 2) * t3.games_left AS ftm,
              round(AVG(t1.fta), 2) * t3.games_left AS fta,
              round(AVG(t1.fg3m), 2) * t3.games_left AS fg3m,
              round(AVG(t1.pts), 2) * t3.games_left AS pts,
              round(AVG(t1.reb), 2) * t3.games_left AS reb,
              round(AVG(t1.ast), 2) * t3.games_left AS ast,
              round(AVG(t1.stl), 2) * t3.games_left AS stl,
              round(AVG(t1.blk), 2) * t3.games_left AS blk,
              round(AVG(t1.tov), 2) * t3.games_left AS tov,
              'Projected' AS stat_type
              FROM nba_players AS t1
              INNER JOIN yahoo_rosters AS t2 ON t1.player_name = t2.player_name
              INNER JOIN games_left_t AS t3 ON t2.player_name = t3.player_name
              GROUP BY t2.owning_team, t1.season_year, t1.player_name,
                  t2.team_name,
              t2.injury_status, t3.games_left
              ORDER BY t2.owning_team
          );
          
          
          DELETE FROM yahoo_matchups
          WHERE stat_type = 'Projected';
          
          
          INSERT INTO yahoo_matchups
          SELECT season, week, week_start, week_end, matchup_number,
          	status, is_playoffs, is_consolation, team_name, team_key,
          0, 0, NULL, 0, 0, NULL, 0, 0, 0, 0, 0, 0, 0, 'Projected'
          FROM yahoo_matchups;
          
          WITH projection_totals AS (
          	SELECT owning_team,
          		sum(fgm) AS fgm, sum(fga) as fga,
          		sum(ftm) as ftm, sum(fta) as fta,
          		sum(fg3m) as fg3m, sum(pts) as pts,
          		sum(reb) as reb, sum(ast) as ast,
          		sum(stl) as stl, sum(blk) as blk,
          		sum(tov) as tov, stat_type
          	FROM projections
          	GROUP BY owning_team, stat_type
          )
          UPDATE yahoo_matchups
          SET fgm = projection_totals.fgm,
          	fga = projection_totals.fga,
          	fg_pct = projection_totals.fgm / projection_totals.fga,
          	ftm = projection_totals.ftm,
          	fta = projection_totals.fta,
          	ft_pct = projection_totals.ftm / projection_totals.fta,
          	fg3m = projection_totals.fg3m,
          	pts = projection_totals.pts,
          	reb = projection_totals.reb,
          	ast = projection_totals.ast,
          	stl = projection_totals.stl,
          	blk = projection_totals.blk,
          	tov = projection_totals.tov
          FROM projection_totals
          WHERE projection_totals.owning_team = yahoo_matchups.team_name
          AND yahoo_matchups.stat_type = 'Projected';
          
          SELECT * FROM yahoo_matchups
          ORDER BY matchup_number, team_key, stat_type;
          """)

try:
        cursor.execute("""
                       {}
                       """.format(query1))
        conn.commit()
        cursor.close()
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: {}".format(error))
    conn.rollback()
    cursor.close()

###
# To do:
###

"""
Either get these in tableau or sql

Calculate a player's games left this week

Calculate a player's season average

Multiply season average by number of games + variable that user can adjust for
number of games
"""

###
# Notes
###

# If we're making the data update automatically, we would want to update daily
# and have yesterday's data updated once. We would then update the current date
# whenever a button is pressed. We could have it refresh every minute as well.