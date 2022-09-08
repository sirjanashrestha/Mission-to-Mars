
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
        'news_title':news_title,
        'news_paragraph':news_paragraph,
        'featured_image':featured_image(browser),
        'facts':mars_facts(),
        'hemispheres':mars_hemis(browser),
        'last_modified':dt.datetime.now()
        }

    #stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    #visit the mars nasa news site
    url='https://redplanetscience.com/'
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
        slide_elem=news_soup.select_one('div.list_text') 
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
    url='https://spaceimages-mars.com'
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
    img_url=f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ### Mars Fact

def mars_facts():
#Scrape entire table data with pandas .read_html function
    try:
        df=pd.read_html('https://galaxyfacts-mars.com')[0] #index 0 only pulls first table panda encounters
    except BaseException:
        return None

    df.columns=['description','Mars','Earth']
    df.set_index('description',inplace=True)

    #convert dataframe back to html ready code
    return df.to_html(classes="table table-striped table-dark")


def mars_hemis(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url) 
    browser.is_element_present_by_css('ul.item_list li.slide',wait_time=1)
    hemisphere_image_urls = []
    
    #parse the html using beautiful soup
    html_link=browser.html
    img_soup=soup(html_link,'html.parser')

    #Get all four hemisphere links
    hemi_links=img_soup.find_all('h3')
    #hemi_link

    for hemi in hemi_links:
        img_page=browser.find_by_text(hemi.text)
        img_page.click()
        html=browser.html
        hemi_soup=soup(html,'html.parser')
        
        #Find the url of full image
        img_url='https://astrogeology.usgs.gov/'+str(hemi_soup.find('img',class_='wide-image')['src'])
        #find the title 
        title=hemi_soup.find('h2',class_='title').text
        
        #Append the hemisphere_img_urls
        hemisphere={'img_url':img_url,'title':title}
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()
    #Print hemisphere image urls
    return hemisphere_image_urls


if __name__=="__main__":
    #If running as script print scraped data
    print(scrape_all())


    