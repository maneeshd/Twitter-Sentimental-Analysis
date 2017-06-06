"""
@author: Maneesh D
@date: 05-Jun-17
@intepreter: Python 3.6.1
"""
from sqlite3 import connect, Error
from sys import exit

from bs4 import BeautifulSoup
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver import Firefox


class ImdbScraper:
    def __init__(self, url="http://m.imdb.com/feature/bornondate"):
        self.__URL = url
        self.__CELEB_LIST = list()

    def __dump_into_db(self):
        """
        Dump the data into db.
        :return: None
        """
        try:
            with connect("./data/celebData.db") as con:
                cur = con.cursor()
                cur.execute("DROP TABLE IF EXISTS CELEB_DATA;")
                cur.execute("CREATE TABLE CELEB_DATA(NAME TEXT, PHOTO TEXT, "
                            "PROFESSION TEXT, BEST_WORK TEXT, SENTIMENT TEXT DEFAULT '');")
                con.commit()

                for celeb in self.__CELEB_LIST:
                    cur.execute("INSERT INTO CELEB_DATA(NAME,PHOTO,PROFESSION,BEST_WORK) "
                                "VALUES(?, ?, ?, ?);",
                                (celeb.get("Name"),
                                 celeb.get("Photo"),
                                 celeb.get("Profession"),
                                 celeb.get("Best Work"),))
                con.commit()
        except Error as e:
            print("SQLITE3 ERROR: %s" % e)
            exit(1)

    def scrape_imdb(self):
        """
        Scrapes the IMDB born_on_date page to collect the top 10 celebrity data.
        After collecting the data stores it in a sqlite3 db.
        :return: None
        """
        try:
            # Initialize the firefox driver.
            driver = Firefox(executable_path="./utils/geckodriver.exe")

            # Run the dynamic content on the webpage.
            driver.get(self.__URL)
            driver.implicitly_wait(30)

            # Get the loaded webpage source.
            page_source = driver.page_source

            # Close the driver.
            driver.close()

            # Create a beautifulsoup crawler and load the page data.
            crawler = BeautifulSoup(page_source, "lxml")

            # Get the required details from the page
            page = crawler.find("section", "posters list")
            born_on_date = page.findChild("h1").text
            print("Getting Data for celebrities born on %s.." % born_on_date)

            # Get the celeb details from HTML and put it in the celeb list
            for link in crawler.find_all("a", class_="poster "):
                celeb = dict()
                # Parse  celeb name
                name = link.find("span", "title").text

                # parse celeb pic
                img = link.img["src"]

                # get profession and best_work
                profession, best_work = link.find("div", "detail").text.split(",")

                # Form a dict for the celeb and push it into celeb list.
                celeb["Name"] = name
                celeb["Photo"] = img
                celeb["Profession"] = profession
                celeb["Best Work"] = best_work
                self.__CELEB_LIST.append(celeb)

            # Dump the data into sqlite3 db
            self.__dump_into_db()

            print("Data Successfully Scraped and dumped into db...")
        except selenium_exceptions as se:
            print("Selenium Exception: %s" % se)
            exit(1)
        except Exception as e:
            print("Exception: %s" % e)
            exit(1)
