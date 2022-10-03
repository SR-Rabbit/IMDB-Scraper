# IMDB-Scraper

## Introduction
A simple web scraper targeted towards scraping the top 1000 movies from IMDB.
The scraped data are then stored in an SQL database managed by SQLite.

This scraper respects robots.txt on IMDB.com, and limits its stress and load on the servers by self imposing delays between obtaining data from each webpage.

## Usage
>Recommended for Python 3.9+.

- Install the dependencies via pip:

`
pip install requirements.txt 
`
- Run IMDBScraper.py
- Wait while data is scraped into an .sqlite file within the same directory as IMDBScraper.py

## Issues
Due to some movies lacking certain attributes (i.e. age ratings, runtime, etc...) the program may encounter issues during the insertion process of the inserting movies data into the database. If so then an AttributeError will be thrown.

## Future Improvements
- Fix issues surrounding movies that lack data
  - Potentially drop incomplete data that are incomplete
- Expand the range of datas to obtain
  - Gross amount made in the box office, etc...
