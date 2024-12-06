# fake python scraper
import requests
from bs4 import BeautifulSoup
import random
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_URI_SCRAPER"))
collection = client["volunteer_system"]["opportunities"]

def scrape():
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    cards = soup.find_all("div", class_="card-content")
    job_type = ["Remote", "On-Site", "Hybrid"]
    time_commitment = ["Full-Time", "Part-time"]

    for card in cards:
        opportunity = {}
        opportunity["title"] = card.find_all("h3", class_="company")[0].text
        opportunity["position"] = card.find_all("h2", class_="title")[0].text
        opportunity["location"] = card.find_all("p", class_="location")[0].text.strip()
        opportunity["description"] = "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Dolor rem ex…"
        opportunity["type"] = job_type[random.randint(0,2)]
        opportunity["link"] = card.find_all("a")[1].get("href")
        opportunity["tim"] = time_commitment[random.randint(0,1)]
        collection.insert_one(opportunity)

scrape()
print("Done!")