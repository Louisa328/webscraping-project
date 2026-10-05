import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import pandas as pd


# Generate 5 URLs of search results.
pages = ['https://sandbox.oxylabs.io/products?page=' + str(i) for i in range(1, 6)]

# Crawl all URLs and extract each product's URL.
product_urls = []
for page in pages:
    print(f'Crawling page \033[38;5;120m{page}\033[0m')
    response = requests.get(page)
    soup = BeautifulSoup(response.text, 'lxml')

    for product in soup.select('.product-card'):
        href = product.find('a').get('href')
        product_urls.append('https://sandbox.oxylabs.io' + href)

print(f'\nFound \033[38;5;229m{len(product_urls)}\033[0m product URLs.')


# Initiliaze a Chrome browser without its GUI.
options = ChromeOptions()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)

# Scrape all product URLs and parse each product's data.
products = []
for i, url in enumerate(product_urls, 1):
    print(f'Scraping URL \033[1;34m{i}\033[0m/{len(product_urls)}.', end='\r')
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    info = soup.select_one('.brand-wrapper')

    product_data = {
        'Title': soup.find('h2').get_text(),
        'Price': soup.select_one('.price').get_text(),
        'Availability': soup.select_one('.availability').get_text(),
        'Stars': len(soup.select('.star-rating > svg')),
        'Description': soup.select_one('.description').get_text(),
        'Genres': ', '.join([genre.get_text().strip() for genre in soup.select('.genre')]),
        'Developer': info.select_one('.brand.developer').get_text().replace('Developer:', '').strip() if info else None,
        'Platform': info.select_one('.game-platform').get_text() if info and info.select_one('.game-platform') else None,
        'Type': info.select('span')[-1].get_text().replace('Type:', '').strip() if info else None
    }
    # Append each product's data to a list.
    products.append(product_data)
driver.quit()

# Save results to a CSV file.
df = pd.DataFrame(products)
df.to_csv('products.csv', index=False, encoding='utf-8')
print('\n\n\033[32mDone!\033[0m Products saved to a CSV file.')