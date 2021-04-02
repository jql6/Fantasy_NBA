# Matchup projections with NBA and Yahoo Fantasy Sports data

[Link to matchup projections graph](https://public.tableau.com/profile/jackie.lu7613#!/vizhome/Projectioncomparisons/Sheet1?publish=yes)

This repo contains the Python scripts I used to scrape NBA and Yahoo Fantasy Sports data into a PostgreSQL database. I used this database to make the [matchup projections Tableau graph](https://public.tableau.com/profile/jackie.lu7613#!/vizhome/Projectioncomparisons/Sheet1?publish=yes).

Credits to [swar](https://github.com/swar) for making the `nba_api` library that I used to pull NBA data. You can find it here: https://github.com/swar/nba_api

Credits to [josuebrunel](https://github.com/josuebrunel) for making the `yahoo_oauth` library that I used to connect to Yahoo's API. You can find it here: https://github.com/josuebrunel/yahoo-oauth

Credits to [rlabausa](https://github.com/rlabausa) for documenting the NBA API endpoints for their schedule data. You can find it here: https://github.com/rlabausa/nba-schedule-data

Credits to [Naysan Saran]() for analyzing the various ways of inserting data into SQL databases with Python via Psycopg2 and writing code for adding values from a data frame into an existing SQL table. You can find the analysis here: https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/ and the code here: https://naysan.ca/2020/06/21/pandas-to-postgresql-using-psycopg2-copy_from/

---

## Usage
