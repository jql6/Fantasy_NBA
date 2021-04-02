# Matchup projections with NBA and Yahoo Fantasy Sports data

[Link to matchup projections graph](https://public.tableau.com/profile/jackie.lu7613#!/vizhome/Projectioncomparisons/Sheet1?publish=yes)

This repo contains the Python scripts I used to scrape NBA and Yahoo Fantasy Sports data into a PostgreSQL database. I used this database to make the [matchup projections Tableau graph](https://public.tableau.com/profile/jackie.lu7613#!/vizhome/Projectioncomparisons/Sheet1?publish=yes).

<details> <summary>References</summary>

Credits to [swar](https://github.com/swar) for making the `nba_api` library that I used to pull NBA data. You can find it here: https://github.com/swar/nba_api

Credits to [josuebrunel](https://github.com/josuebrunel) for making the     `yahoo_oauth` library that I used to connect to Yahoo's API. You can find it here: https://github.com/josuebrunel/yahoo-oauth

Credits to [rlabausa](https://github.com/rlabausa) for documenting the NBA API endpoints for their schedule data. You can find it here: https://github.com/rlabausa/nba-schedule-data

Credits to [Naysan Saran](https://naysan.ca/) for analyzing the various ways of inserting data into SQL databases with Python via Psycopg2 and writing code for adding values from a data frame into an existing SQL table. You can find the analysis here: https://naysan.ca/2020/05/09/ pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/ and the code here: https://naysan.ca/2020/06/21/  pandas-to-postgresql-using-psycopg2-copy_from/
</details>
---

## Usage

* Get your league id. If you don't know how, run `python data_scraper.py` and enter `1` for the script to take you to the website to find your league id. Once your browser is open, you can stop the script.
* Go into `data_scraper.py`, search "# Add your league id here" and add your league id.
* Set up your local PostgreSQL server and create a database.
* Make your `private.json` and `sql_login.json` files. You can do so by copying and renaming the examples that I've provided, and then editing the relevant fields.
* Run `python data_scraper.py`. You should now have the relevant csv files and should be able to connect to your SQL data with Tableau to plot it.