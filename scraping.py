
#Import scraping tools
from splinter import Browser
from bs4 import BeautifulSoup as soup
#Import dependencies
import pandas as pd
import datetime as dt

from webdriver_manager.chrome import ChromeDriverManager



#create a function that initialize the browser, create data dictionary, return
#the scraped data and end the webdriver
def scrape_all():

    #Initiate headless driver for deployment
    executable_path={'executable_path':ChromeDriverManager().install()}
    browser=Browser('chrome',**executable_path,headless=True)

    news_title,news_paragraph=mars_news(browser)
    #Run all scraping functions and store results in dictionary
    data={
        "news_title":news_title,
        "news_paragraph":news_paragraph,
        "featured_image":featured_image(browser),
        "facts":mars_facts(),
        "last_modified":dt.datetime.now()
        }

    #stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    #visit the mars nasa news site
    url='https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    #delay for loading the page
    browser.is_element_present_by_css('div.list_text',wait_time=1)

    #Parse the html
    html=browser.html
    news_soup=soup(html,'html.parser')
    
    # ### Mars Data:News
    #Add try/except for error handling
    try:

        #Assign title and summary text to variable
        slide_elem=news_soup.select_one('div.list_text') #declare variable to look for <div/> tag and its descendents

        #Return only title of the article not any html tags or elements
        news_title=slide_elem.find('div',class_='content_title').get_text()
    
        #Find the paragraph text
        news_p=slide_elem.find('div',class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None,None
    
    return news_title,news_p

#### Featured Images

def featured_image(browser):
    #Visit URL
    url='https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem=browser.find_by_tag('button')[1]
    full_image_elem.click()

    #Parse the html
    html=browser.html
    img_soup=soup(html,'html.parser')

    try:
        #Find the related image URL
        img_url_rel=img_soup.find('img',class_='fancybox-image').get('src')

    except AttributeError:
        return None

        #Use base URL to create an absolute URL
    img_url=f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url


# ### Mars Fact

def mars_facts():
#Scrape entire table data with pandas .read_html function
    try:
        df=pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0] #index 0 only pulls first table panda encounters

    except BaseException:
        
        return None

    df.columns=['description','Mars','Earth']
    df.set_index('description',inplace=True)

    #convert dataframe back to html ready code
    return df.to_html(classes="table table-striped")


if __name__=="__main__":
    #If running as script print scraped data
    print(scrape_all())