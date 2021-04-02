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
- [Intro](#intro)
- [Set up](#set-up)
- [Directions](#directions)
- [Notes](#notes)
- [References](#references)

# Intro
I will discuss how I gathered the data, my thought process on the data scraping, and how I dealt with some of the issues I had with PostgreSQL and Tableau.

# Set up
You'll need Conda, a Hashtag Basketball account with your league set up already, and a Yahoo Fantasy Sports account. see [References](#references) for the links. With Conda, you'll need to create a new environment and install the Selenium package.

# Directions
In Terminal, change directories into the directory containing the `.py` file. Activate the Conda environment that you made and then run the file with `python hashtag_bball_bot.py`. When the script is finished, you should have a `rankings.csv` file in your directory.

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