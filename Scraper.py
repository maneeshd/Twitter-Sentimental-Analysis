"""
@author: Maneesh D
@date: 05-Jun-17
"""
from sqlite3 import connect, Error
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox


class ImdbScraper:
    """
    Scrape IMDb for Celebrity Data.
    """
    def __init__(self, url="http://m.imdb.com/feature/bornondate"):
        """
        Constructor
        :param url: URL for the IMDb page.
        """
        self.__url = url
        self.__celeb_list = list()

    def __dump_into_db(self):
        """
        Dump the data into db.
        :return: None
        """
        try:
            with connect("./data/celebData.db") as con:
                cur = con.cursor()
                cur.execute("DROP TABLE IF EXISTS CELEB_DATA;")
                cur.execute("CREATE TABLE CELEB_DATA("
                            "NAME TEXT, "
                            "PHOTO TEXT, "
                            "PROFESSION TEXT, "
                            "BEST_WORK TEXT, "
                            "SENTIMENT TEXT DEFAULT '');")
                con.commit()

                for celeb in self.__celeb_list:
                    cur.execute("INSERT INTO CELEB_DATA(NAME,"
                                "PHOTO,"
                                "PROFESSION,"
                                "BEST_WORK) "
                                "VALUES(?, ?, ?, ?);",
                                (celeb.get("Name"),
                                 celeb.get("Photo"),
                                 celeb.get("Profession"),
                                 celeb.get("Best Work"),))
                con.commit()
        except Error as err:
            print("!!! SQLITE3 ERROR: %s !!!" % err)
            exit(1)

    def scrape_imdb(self):
        """
        Scrapes the IMDB born_on_date page to collect the top 10
        celebrity data.After collecting the data stores it in a sqlite3 db.
        :return: None
        """
        try:
            # Initialize the firefox driver.
            driver = Firefox(executable_path="./utils/geckodriver.exe")

            # Run the dynamic content on the webpage.
            driver.get(self.__url)
            driver.implicitly_wait(30)

            # Get the loaded webpage source.
            page_source = driver.page_source

            # Close the driver.
            driver.close()

            # Create a beautifulsoup crawler and load the page data.
            try:
                crawler = BeautifulSoup(page_source, "lxml")
            except Exception:
                crawler = BeautifulSoup(page_source, "html.parser")

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
                profession, best_work = link.find("div",
                                                  "detail").text.split(",")

                # Form a dict for the celeb and push it into celeb list.
                celeb["Name"] = name
                celeb["Photo"] = img
                celeb["Profession"] = profession
                celeb["Best Work"] = best_work
                self.__celeb_list.append(celeb)

            # Dump the data into sqlite3 db
            self.__dump_into_db()

            print("Data Successfully Scraped and dumped into db...")
        except Exception as exp:
            print("Exception: %s" % exp)
            exit(1)
