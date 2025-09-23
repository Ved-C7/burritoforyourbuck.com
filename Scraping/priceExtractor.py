from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
driver_path = '/Users/vedchidrawar/Downloads/chromedriver-mac-arm64/chromedriver'  # Update the path as per your location
base_url = 'https://www.chipotle.com/?utm_source=locationpage&utm_medium=yext&utm_campaign=order_online_hero&restaurant='
menu_types = ['burrito', 'burrito-bowl', 'quesadilla']
# store_codes = ['3804', '1234', '5678']  # Example store codes

# Function to read store codes from a file
def read_store_codes(file_path):
    with open(file_path, 'r') as file:
        store_codes = [line.strip() for line in file if line.strip().isdigit()]
    return store_codes

# Read store codes from the text file
store_codes = read_store_codes('store_numbers.txt')


# Initialize the WebDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

def get_prices(store_code):
    # Navigate to the store page
    store_url = f"{base_url}{store_code}"
    driver.get(store_url)
    
    # Wait for the initial page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".top-level-menus"))
    )

    # Collect data for each menu type
    prices = {}
    for menu_type in menu_types:
        menu_url = f"https://www.chipotle.com/order/build/{menu_type}"
        driver.get(menu_url)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".meal-builder-item-selector-card-container"))
            )
        except TimeoutException:
            print(f"Timed out waiting for {menu_type} page to load")
            continue

        # Debugging: Print page source or take a screenshot
        with open(f"{menu_type}_page_source.html", "w") as file:
            file.write(driver.page_source)
        driver.save_screenshot(f"{menu_type}_screenshot.png")

        # Extract prices
        try:
            items = driver.find_elements(By.CSS_SELECTOR, ".meal-builder-item-selector-card-container")
            for item in items:
                name = item.get_attribute("data-qa-item-name")
                if 'Chicken al Pastor' in name:
                    continue  # Skip Chicken al Pastor as per your request
                price = item.find_element(By.CSS_SELECTOR, ".item-cost").text
                prices[f"{menu_type} - {name}"] = price
        except NoSuchElementException:
            print(f"Could not find price element for {menu_type}")

    return prices
# Function to save collected data to a text file
def save_prices_to_file(all_prices, file_path):
    with open(file_path, 'w') as file:
        for store, prices in all_prices.items():
            file.write(f"Store {store}:\n")
            for item, price in prices.items():
                file.write(f"{item}: {price}\n")
            file.write("\n")

# Collect data from each store
all_prices = {}
for code in store_codes:
    all_prices[code] = get_prices(code)

# Close the driver
driver.quit()

# Save collected data to a text file
save_prices_to_file(all_prices, 'collected_prices.txt')

# Print collected data
for store, prices in all_prices.items():
    print(f"Store {store}:")
    for item, price in prices.items():
        print(f"{item}: {price}")