import requests
from bs4 import BeautifulSoup

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def scrape_store_numbers(state_urls):
    store_details = []

    for state_url in state_urls:
        state_soup = get_soup(state_url)
        city_links = state_soup.find_all('a', class_='Directory-listLink')

        for city_link in city_links:
            city_url = state_url.rstrip('/') + city_link['href']
            city_soup = get_soup(city_url)
            # Check if the city has multiple stores
            if 'data-count' in city_link.attrs:
                count = int(city_link['data-count'].strip('()'))
                if count > 1:
                    # Navigate into the city page if multiple stores
                    store_links = city_soup.find_all('a', class_='Teaser-titleLink')
                    for store_link in store_links:
                        store_url = city_url.rstrip('/') + store_link['href'].replace('..', '')
                        store_soup = get_soup(store_url)
                        store_detail = extract_store_details(store_soup)
                        store_details.append(store_detail)
                        print(store_detail)
                else:
                    # Single store, extract directly
                    store_detail = extract_store_details(city_soup)
                    store_details.append(store_detail)
                    print(store_detail)
            else:
                # Single store, extract directly
                store_detail = extract_store_details(city_soup)
                store_details.append(store_detail)

    return store_details

def extract_store_details(soup):
    # Extract store number from the "Order Online" button's URL
    order_online_button = soup.find('a', class_='Core-cta--online')
    if order_online_button and 'href' in order_online_button.attrs:
        url = order_online_button['href']
        # Extract the store number from the URL query parameter 'restaurant'
        store_number = url.split('restaurant=')[-1]
    else:
        store_number = 'Number not found'

    # Extract address details
    address_tag = soup.find('address', class_='c-address')
    if address_tag:
        street_address = address_tag.find('span', class_='c-address-street-1').text.strip()
        city = address_tag.find('span', class_='c-address-city').text.strip()
        state = address_tag.find('abbr', class_='c-address-state').text.strip()
        postal_code = address_tag.find('span', class_='c-address-postal-code').text.strip()
        full_address = f"{street_address}, {city}, {state} {postal_code}"
    else:
        full_address = 'Address not found'

    return f"{store_number} - {full_address}"

# URLs for South Dakota and North Dakota
state_urls = [
    'https://locations.chipotle.com/sd',
    'https://locations.chipotle.com/nd'
]

store_details = scrape_store_numbers(state_urls)
with open('Dakotas.txt', 'w') as file:
    for detail in store_details:
        print(detail)
        file.write(detail + '\n')

print("Store details have been saved to Dakotas.txt")
