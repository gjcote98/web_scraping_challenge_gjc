from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app=Flask(__name__)

mongo=PyMongo(app,uri="mongodb://localhost:27017/mars")

@app.route("/")
def home():
    mars=mongo.db.mars.find_one()
    return render_template("index.html",mars=mars)

@app.route("/scrape")
def scraper():
    mars=mongo.db.mars
    mars_data=scrape_mars.scrape_info()
    mars.update({},mars_data, upsert=True)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
