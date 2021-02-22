from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

def get_url(search_word, market_place, npage=1):
    """..................."""
    template = 'https://www.amazon.{}/s?k={}&page={}&ref=nb_sb_noss_2'
    search_word = search_word.replace(' ', '+')
    return template.format(market_place,search_word,npage)





def get_all_info(results, bsellerRank, market_place):
    ## Working 
    """ For This Function it work just for Bookes T-shirt but i try to use it for toys it doesn't work because toys Information about the seller is 
    on Table but Bookes and other category the information on list format
    """
    data = {
        'title': [],
        'best_seller': [],
        'rating': [],
        'categories_ranked': [],
        'link_of_product': [],
        'image_link': [],
        'sponsor': []
    }
    
    sub_driver = webdriver.Chrome('/Users/Mehdi/Documents/ChromDriver/chromedriver')
    HeadUrl= 'https://www.amazon.'+market_place
    for res in results:
        try:
            Link = HeadUrl+res.h2.a.get('href')
            sub_driver.get(Link)
            sub_soup = BeautifulSoup(sub_driver.page_source, 'html.parser')
            info = sub_soup.find_all('ul', {'class' : 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})[1]
            li_txt = info.li.text.strip()
            index_Of_Sharp = li_txt.find('#')
            index_space = li_txt[index_Of_Sharp:].find(' ')
            bseller = info.li.text.strip()[index_Of_Sharp+1: index_Of_Sharp+index_space].replace(',', '')
            if bseller.strip().isdigit():
                #print(int(bseller))
                if int(bseller) <= bsellerRank:
                    ## Get all informatin about the product
                    try:
                        title = sub_soup.find('h1', {'id' : 'title'}).text.strip() #Title
                    except:
                        title='null'
                    finally:
                        data['title'].append(title)
                    
                    
                    try:
                        rating = sub_soup.find('span', {'id' : 'acrCustomerReviewText'}).text
                    except:
                        rating = 'null'
                    finally:
                        data['rating'].append(rating) #rating
                    try:
                        img_link = sub_soup.find('div', {'id' : 'main-image-container'}).img.get('src')
                    except:
                        img_link = 'null'
                    finally:
                        data['image_link'].append(img_link)
                        
                    try:
                        ranking_caterogy = li_txt[index_Of_Sharp:].strip()# ranked categories
                    except:
                        ranking_caterogy = 'null'
                    finally:
                         data['categories_ranked'].append(ranking_caterogy)
                                      
                    data['best_seller'].append(int(bseller))
                    
                    data['link_of_product'].append(Link)
                    data['sponsor'].append('spons' in Link)
        except:
            pass
            ## if not just skip it
    return data                            






def loop_in_pages(keywords, minBseller, market_place='com'):
    try:
        driver = webdriver.Chrome('/Users/Mehdi/Documents/ChromDriver/chromedriver')
        url = get_url(keywords, market_place)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        nbr_pages = int(soup.find('li', {'class': 'a-disabled', 'aria-disabled': 'true'}).text.strip())
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        data = get_all_info(results, minBseller, market_place)
        for page in range(2,3):
            try:
                url = get_url(keywords, page)
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                results = soup.find_all('div', {'data-component-type': 's-search-result'})
                dt = get_all_info(results, minBseller)
                data['title'] += dt['title']
                data['rating']+= dt['rating']
                data['image_link'] += dt['image_link']
                data['categories_ranked'] += dt['categories_ranked']
                data['best_seller'] += dt['best_seller']
                data['link_of_product'] += dt['link_of_product']
            except:
                pass
    except:
        return data
    return data




if __name__ == '__main__':
    keywords = input('Keywords: ')
    minBseller = int(input('Min Ranked Best Seller: '))
    data = loop_in_pages(keywords, minBseller)
    data = pd.DataFrame(data)
    data.to_csv('Best_seller_amazon.csv')