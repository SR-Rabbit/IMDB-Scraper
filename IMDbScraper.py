import sqlite3
import random
import urllib.robotparser
import time
import configparser
import requests
from bs4 import BeautifulSoup


class Scraper:
    """Scrapes movie data from IMDb"""

    config = configparser.ConfigParser()
    config.read("ScraperHeader.ini")
    user_agents = config["HeaderConfiguration"]["UserAgents"]
    proxy_list = config["HeaderConfiguration"]["Proxies"]
    rand_proxy = random.choice(list(proxy_list.split(","))).strip()

    def __init__(self) -> None:
        self.web_header = {
            "Accept-Language": "en-US,en;q=0.5",
            "user-agent": random.choice(list(self.user_agents.split(","))).strip(),
        }
        self.web_proxy = {"http": f"http://{self.rand_proxy}"}
        self.baseurl = "https://www.imdb.com"

    def scraper_delay(self):
        """Delays the program in making a request as to not overload web server."""
        message = "----------------\nCONSTRUCTING URL\n----------------"
        for character in message:
            print(character, end="")
            time.sleep(0.5)
        print("")

    def robot_obey(self, url) -> bool:
        """Checks the 'robots.txt' and adheres to its restrictions."""
        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.set_url(f"{self.baseurl}/robots.txt")
        robot_parser.read()
        return bool(robot_parser.can_fetch("*", url))

    def url_builder(self, url_value) -> str:
        """Constructs the url to navigate through the webpage."""
        result_url = f"https://www.imdb.com/search/title/?groups=top_1000&start={url_value}&ref_=adv_nxt"
        return result_url

    def get_webpage(self, url):
        """Makes a request and obtains data from specified url."""
        web_page = requests.get(url, headers=self.web_header, proxies=self.web_proxy)
        return web_page

    def soupify_webpage(self, web_page):
        """Creates and Returns 'soup' of requested url."""
        soup = BeautifulSoup(web_page.text, "html.parser")
        return soup

    def scrape_main(self, soup) -> dict:
        """Scrapes movie title, URL, year of release, age rating, runtime, genre and metascore."""
        movies_dict = {}
        data_list = []
        mvs = Scraper()
        main_div = soup.find("div", class_="lister-list")
        all_items_div = main_div.find_all("div", class_="lister-item mode-advanced")
        for elements in all_items_div:
            movie_id_title = mvs.scrape_unique(elements)
            movie_year = mvs.scrape_year(elements)
            movie_age = mvs.scrape_age(elements)
            movie_runtime = mvs.scrape_runtime(elements)
            movie_genre = mvs.scrape_genre(elements)
            movie_metascore = mvs.scrape_metascore(elements)
            movie_rating = mvs.scrape_rating(elements)
            movie_staff = mvs.scrape_staffs(elements)
            data_list = [
                movie_id_title[0],
                movie_year,
                movie_age,
                movie_runtime,
                movie_genre,
                movie_metascore,
                movie_rating,
                movie_staff,
            ]
            movies_dict[movie_id_title[1]] = data_list
        return movies_dict

    def scrape_unique(self, elements: str) -> tuple:
        """Scrapes the title and unique ID of a movie."""
        try:
            t_element = elements.find("h3", class_="lister-item-header")
            unique_tag = t_element.find("a")
            movie_id = unique_tag["href"][9:16]
            movie_title = unique_tag.text
        except AttributeError:
            movie_id = "N/A"
            movie_title = "N/A"
        return movie_id, movie_title

    def scrape_year(self, elements):
        """Scrapes the release year of a movie."""
        try:
            t_element = elements.find("h3", class_="lister-item-header")
            year_element = t_element.find(
                "span", class_="lister-item-year text-muted unbold"
            )
            movie_year = year_element.text[1:-1]
        except AttributeError:
            movie_year = "N/A"
        return movie_year

    def scrape_age(self, elements):
        """Scrapes the age rating of a movie."""
        try:
            i_element = elements.find("p", class_="text-muted")
            age_element = i_element.find("span", class_="certificate")
            movie_age_rating = age_element.text
        except AttributeError:
            movie_age_rating = "N/A"
        return movie_age_rating

    def scrape_runtime(self, elements):
        """Scrapes the runtime of a movie."""
        try:
            i_element = elements.find("p", class_="text-muted")
            runtime_element = i_element.find("span", class_="runtime")
            movie_runtime = runtime_element.text[:-4]
        except AttributeError:
            movie_runtime = "N/A"
        return movie_runtime

    def scrape_genre(self, elements):
        """Scrapes the genre of a movie."""
        try:
            i_element = elements.find("p", class_="text-muted")
            genre_element = i_element.find("span", class_="genre")
            movie_genre = genre_element.text.strip()
        except AttributeError:
            movie_genre = "N/A"
        return movie_genre

    def scrape_metascore(self, elements):
        """Scrapes the metascore of a movie."""
        try:
            r_element = elements.find("div", class_="ratings-bar")
            metascore_element = r_element.find("span", class_="metascore")
            movie_metascore = metascore_element.text.strip()
        except AttributeError:
            movie_metascore = "N/A"
        return movie_metascore

    def scrape_rating(self, elements):
        """Scrapes the ratings of a movie."""
        try:
            r_element = elements.find("div", class_="ratings-bar")
            rating_element = r_element.find("strong")
            movie_rating = rating_element.text
        except AttributeError:
            movie_rating = "N/A"
        return movie_rating

    def scrape_staffs(self, elements):
        staff_list = []
        try:
            staffs = elements.find("p", class_="")
            person_results = staffs.find_all("a")
            staff_list.extend(person.text for person in person_results)
        except AttributeError:
            staff_list = "N/A"
        return staff_list

    def create_database(self, database_name: str) -> None:
        """Creates a database."""
        conn = sqlite3.connect(f"{database_name}.sqlite")
        cur = conn.cursor()
        cur.executescript(
            """
        CREATE TABLE IF NOT EXISTS Main(
        id                  INTEGER NOT NULL PRIMARY KEY,
        movieinfo_id        INTEGER,
        release_year        TEXT,
        runtime             TEXT,
        age_rating          TEXT,
        imdb_rating         TEXT,
        metascore           TEXT
        );

        CREATE TABLE IF NOT EXISTS MovieInfo(
        id      INTEGER NOT NULL PRIMARY KEY,
        title   TEXT UNIQUE,
        url     TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Genre(
        id      INTEGER NOT NULL PRIMARY KEY,
        type    TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Genre_Link(
        genre_id    INTEGER,
        main_id     INTEGER,
        PRIMARY KEY(main_id, genre_id)
        );

        CREATE TABLE IF NOT EXISTS Staff(
        main_id     INTEGER,
        people_id   INTEGER,
        PRIMARY KEY (main_id, people_id)
        );

        CREATE TABLE IF NOT EXISTS People(
        id      INTEGER NOT NULL PRIMARY KEY,
        name    TEXT UNIQUE
        );
        """
        )
        return None

    def database_insert(self, database_name: str, movie_dict: dict) -> None:
        """Inserts scraped data into respective tables within the database."""
        conn = sqlite3.connect(f"{database_name}.sqlite")
        cur = conn.cursor()
        for key, value in movie_dict.items():
            cur.execute(
                "INSERT OR IGNORE INTO MovieInfo (title, url) VALUES (?, ?)",
                (key, value[0]),
            )
            cur.execute("SELECT id FROM MovieInfo WHERE url = ?", (value[0],))
            print(value[0])
            movieinfo_id = cur.fetchone()[0]
            print(movieinfo_id)
            cur.execute(
                "INSERT OR IGNORE INTO Main (movieinfo_id, release_year, age_rating, runtime, imdb_rating, metascore) VALUES (?,?,?,?,?,?)",
                (movieinfo_id, value[1], value[2], value[3], value[6], value[5]),
            )
            cur.execute(
                "SELECT id FROM Main WHERE release_year = ? AND runtime = ?",
                (value[1], value[3]),
            )
            main_id = cur.fetchone()[0]
            # Unable to retireve ID due to missing values in the WHERE's, or unable to take in "N/A" as a value
            for genres in value[4].split(", "):
                cur.execute("INSERT OR IGNORE INTO Genre (type) VALUES(?)", (genres,))
                cur.execute("SELECT id FROM Genre WHERE type = ?", (genres,))
                genre_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT OR IGNORE INTO Genre_Link (main_id, genre_id) VALUES (?,?)",
                    (main_id, genre_id),
                )

            for people in value[7]:
                cur.execute("INSERT OR IGNORE INTO People (name) VALUES(?)", (people,))
                cur.execute("SELECT id FROM People WHERE name = ?", (people,))
                people_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT OR IGNORE INTO Staff (main_id, people_id) VALUES (?, ?)",
                    (main_id, people_id),
                )

        conn.commit()
        return None

    def search_movie(self, database_name: str) -> None:
        """Obtains unique url from database to be constructed then scraped."""
        conn = sqlite3.connect(f"{database_name}.sqlite")
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, url, status FROM MovieInfo WHERE status = 0 LIMIT 1"
        )
        result = cur.fetchone()
        cur.execute("UPDATE MovieInfo Set status = ? WHERE id = ?", (1, result[0]))
        conn.commit()
        return result[2]


# ------------ Testing Area ------------ #

db_name = "MovieTitles"
MovieScraper = Scraper()
MovieScraper.create_database(db_name)
for num_set in range(1, 952, 50):
    # MovieScraper.scraper_delay()
    time.sleep(4)
    top_url = MovieScraper.url_builder(num_set)
    if MovieScraper.robot_obey(top_url) is True:
        print("----------------\nSCRAPING ALLOWED\n----------------")
        movie_webpage = MovieScraper.get_webpage(top_url)
        returned_soup = MovieScraper.soupify_webpage(movie_webpage)
        scrape_result = MovieScraper.scrape_main(returned_soup)
        MovieScraper.database_insert(db_name, scrape_result)
        # print(scrape_result)
    else:
        print("----------------\nSCRAPING DISALLOWED\n----------------")
        break

# ---------------------
# - Join tables together at the end to display all relevant data.

# FUTURE IMPROVEMENTS
# - Scrape the gross amount made by the movie if available.
