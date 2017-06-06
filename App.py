"""
@author: Maneesh D
@date: 05-Jun-17
@intepreter: Python 3.6.1

Application to scrape IMDb for celebrity details and then perform Sentiment
Analysis on the celebrities on Twitter
"""
from sqlite3 import connect
try:
    from json import dump
except ImportError:
    from simplejson import dump
from datetime import datetime
from os import getcwd

Scraper = __import__("Scraper")
Sentiment = __import__("TwitterSentiment")
URL = "http://m.imdb.com/feature/bornondate"


def main():
    print("TWITTER SENTIMENTAL ANALYSIS")
    print("-" * len("TWITTER SENTIMENTAL ANALYSIS"))

    # get the scraper object to scrape IMDb
    my_scraper = Scraper.ImdbScraper(URL)
    print("Scraping IMDb...Please wait...")
    my_scraper.scrape_imdb()
    print("Successfully scraped IMDb...\n")

    # Perforn Twitter Sentiment Analysis
    sentiment_analyzer = Sentiment.TwitterSentiment()
    result = sentiment_analyzer.get_twitter_sentiment()
    if result == -1:
        print("Twitter Sentiment Analysis Failed...")
        exit(1)
    print("\nThe Twitter Sentiment Result:")
    print("-" * len("The Twitter Sentiment Result:"))
    try:
        with connect("./data/celebData.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM CELEB_DATA;")    # Get the result data from db and print.
            celeb_list = list()
            for row in cur.fetchall():
                celeb = dict()

                print("Name: %s" % row[0])
                celeb["name"] = row[0]

                print("Photo: %s" % row[1])
                celeb["Photo"] = row[1]

                print("Profession: %s" % row[2])
                celeb["Profession"] = row[2]

                print("Best Work: %s" % row[3])
                celeb["Best Work"] = row[3].replace('"', "")

                print("Overall Twitter Sentiment: %s\n" % row[4])
                celeb["Twitter Sentiment"] = row[4]

                celeb_list.append(celeb)
        
        # Dump the results into a JSON file.
        suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = "Sentiment-Analysis-Result_%s.json" % suffix

        with open("./results/%s" % file_name, "w") as fs:
            dump(celeb_list, fs, ensure_ascii=True, indent=2)

        print("Result JSON created: %s" % (getcwd() + file_name))
    except Exception as e:
        print("An Exception Occurred:\n%s" % e)
        exit(1)
    print("THANK YOU")
    return 0

if __name__ == '__main__':
    main()
