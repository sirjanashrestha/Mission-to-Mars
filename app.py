from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
import scraping

### set up Flask
app=Flask(__name__)

## Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"]="mongodb://localhost:27017/mars_app"
mongo=PyMongo(app)

#define the route for HTML page
@app.route("/") #tells what to display when we are looking at the hoje page,index.html
def index(): 
    mars=mongo.db.mars.find_one() #find mars collection in database
    return render_template("index.html",mars=mars) #return html template using
    #index.html file, using mars collection in mongodb

@app.route("/scrape")
def scrape():
    mars=mongo.db.mars #assign new variable that points to our Mongo db
    mars_data=scraping.scrape_all() #create new variable to hold newly scraped data,scrape_all function in the scraping.py file
    mars.update_one({},mars_data,upsert=True) #update the database #upsert creates newdatabase if one doesnot already exists
    return redirect('/',code=302)

if __name__=="__main__":
    app.run()
