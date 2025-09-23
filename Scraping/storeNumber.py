import requests
from bs4 import BeautifulSoup

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def scrape_store_numbers(base_url):
    main_page = get_soup(base_url)
    state_links = main_page.find_all('a', class_='Directory-listLink')
    store_numbers = []

    for link in state_links:
        state_url = base_url + link['href']
        state_soup = get_soup(state_url)
        city_links = state_soup.find_all('a', class_='Directory-listLink')

        for city_link in city_links:
            city_url = base_url + city_link['href']
            city_soup = get_soup(city_url)
            # Check if the city has multiple stores
            if 'data-count' in city_link.attrs:
                count = int(city_link['data-count'].strip('()'))
                if count > 1:
                    # Navigate into the city page if multiple stores
                    store_links = city_soup.find_all('a', class_='Teaser-titleLink')
                    for store_link in store_links:
                        store_url = base_url + store_link['href'].replace('..', '')
                        store_soup = get_soup(store_url)
                        store_number = extract_store_number(store_soup)
                        store_numbers.append(store_number)
                        print(store_number)
                else:
                    # Single store, extract directly
                    store_number = extract_store_number(city_soup)
                    store_numbers.append(store_number)
                    print(store_number)
            else:
                # Single store, extract directly
                store_number = extract_store_number(city_soup)
                store_numbers.append(store_number)

    return store_numbers

def extract_store_number(soup):
    # Extract store number from the "Order Online" button's URL
    order_online_button = soup.find('a', class_='Core-cta--online')
    if order_online_button and 'href' in order_online_button.attrs:
        url = order_online_button['href']
        # Extract the store number from the URL query parameter 'restaurant'
        store_number = url.split('restaurant=')[-1]
        return store_number
    return 'Number not found'

base_url = 'https://locations.chipotle.com/'  # Main URL for all locations
store_numbers = scrape_store_numbers(base_url)
with open('store_numbers.txt', 'w') as file:
    for number in store_numbers:
        file.write(number + '\n')

print("Store numbers have been saved to store_numbers.txt")