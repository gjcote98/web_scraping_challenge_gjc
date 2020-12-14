import pymongo
from flask_pymongo import PyMongo
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from flask import Flask, render_template, redirect
from webdriver_manager.chrome import ChromeDriverManager
import time

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    news_url = 'https://mars.nasa.gov/news/'
    response = requests.get(news_url)
    news_soup = bs(response.text, 'html.parser')

    title = news_soup.find_all('div', class_="content_title")[0].text
    title = title.strip('\n\n')
    paragraph = news_soup.find_all('div',class_="rollover_description_inner")[0].text
    paragraph = paragraph.strip('\n\n')
    
    img_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(img_url)
    img_html=browser.html
    img_soup=bs(img_html,"html.parser")

    feature_image=img_soup.find_all('article',class_="carousel_item")[0]['style']
    feature_image=feature_image.strip("'background-image: url('/")
    feature_image=feature_image.strip("');")
    featured_image_url='https://www.jpl.nasa.gov/'+feature_image

    facts_url="https://space-facts.com/mars/"
    time.sleep(1)
    browser.visit(facts_url)
    time.sleep(1)
    facts=pd.read_html(facts_url)
    facts_df=facts[0]
    facts = facts_df.rename(columns={0 : "Features", 1 : "Value"}).set_index(["Features"])
    facts = facts.to_html(classes="table table-striped")

    hem_url= 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hem_url)
    hem_html = browser.html
    hem_soup = bs(hem_html, 'html.parser')
    hem = hem_soup.find('div', class_='collapsible results')
    hemispheres=hem.find_all('a')
    hemisphere_img_urls = []

    for hemisphere in hemispheres:
        if hemisphere.h3:
            title=hemisphere.h3.text
            link=hemisphere["href"]
            main_url="https://astrogeology.usgs.gov/"
            next_url=main_url+link
            browser.visit(next_url)
            hem_img_html = browser.html
            hem_img_soup = bs(hem_img_html, 'html.parser')
            hem_img=hem_img_soup.find("div",class_= "downloads")
            img=hem_img.ul.a["href"]
            hemisphere_dict={}
            hemisphere_dict["Title"]=title
            hemisphere_dict["Image_URL"]=img
            hemisphere_img_urls.append(hemisphere_dict)
            browser.back()

    mars_dict={"title":title,
        "paragraph":paragraph,
        "featured_img": featured_image_url,
        "facts": facts,
        "hemisphere":hemisphere_img_urls
        }

    browser.quit()

    return mars_dict
