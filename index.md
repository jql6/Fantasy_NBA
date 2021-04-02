<head>
  <!-- style sheet -->
  <style type = text/css>
    body{
        color: white;
        background-color: rgb(60, 60, 60);
    }

<!-- I don't know why, but both `a` and `a:link` must be changed -->
<!-- to change link colors -->
    a{ color: rgb(97, 175, 239) !important; }
    a:link{ color: rgb(97, 175, 239) !important; }
    a:visited{ color: rgb(230, 180, 180) !important; }

    :is(h1, h2, h3, h4, h5, h6, p) { color: white; }

    code{
        margin-left: 0.2em;
        margin-right: 0.2em;
        outline-style: solid;
        outline-color: rgb(160, 160, 160);
        outline-width: 1px;
        outline-offset: 1px;
        background-color: rgb(50, 50, 50);
    }

    pre code{
      margin-left: 0em;
      margin-right: 0em;
    }
  </style>
</head>

<!-- omit in toc -->
# Yahoo matchup projections with NBA data
<!-- omit in toc -->
## Author: Jackie Lu
<!-- omit in toc -->
## Date: 2021, Apr. 1

<section class="footer">
  <p>
    <a href="https://github.com/jql6/Fantasy_NBA">
      Link to the repository
    </a> | 
    <a href="https://jql6.github.io/">
      Return to homepage
    </a>
  </p>
</section>

<!-- omit in toc -->
## Table of Contents
- [Set up](#set-up)
- [Data](#data)
- [Notes](#notes)
- [References](#references)

# Set up
Here is the [link to the graph](https://public.tableau.com/profile/jackie.lu7613#!/vizhome/Projectioncomparisons/Sheet1?publish=yes) if you just want to look at it.

If you want to pull the data for yourself, you'll need a Python environment with the libraries I import from the Python files. You can make the environment with the `requirements.txt` file. You'll also need the league id of your Yahoo Fantasy Sports league. This can be found by logging in online and checking your league settings. There should be a field there that shows you what your league id is. Finally, you'll also need [PostgreSQL](https://www.postgresql.org/download/). For this project, I used a local PostgreSQL server.

# Data
There are four scraped data sets. The first is the Yahoo Fantasy Sports matchups data which lists the different teams in your league and who they're matched up against.

The second is the Yahoo Fantasy Sports roster data which displays the players and teams in the league that have these players rostered.

The third data set is the playergamelogs dataset from NBA API. This is a large dataframe of all of the boxscores for every player during the season. We can use this data to calculate the season averages for rostered players.

The fourth data set is the nba schedule data. The data comes with a column indicating whether or not the game is finished or not. This allows us to calculate how many games a team has left for the week.

<details><summary>Note about playergamelogs</summary>
I used playergamelogs instead of individually selecting players from playergamelog because NBA API requires a cooldown between requests. Getting the data for all players is faster here because you only need one request.
</details>

# Notes
Sometimes the script will fail due to a timeout near the yahoo login steps. You can just try the script again.

# References
1. [Conda installation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. [Hashtag Basketball](https://hashtagbasketball.com/)
3. [Yahoo Fantasy Sports](https://sports.yahoo.com/fantasy/)
4. [Chromedriver](https://chromedriver.chromium.org/)


<br>
<br>
<br>
<br>
<!-- Using four breaks here so that when you scroll all the way down -->
<!-- the text content won't be stuck at the very bottom of the screen. -->
<!-- Creating table of contents with Markdown All in One by Yu Zhang. -->