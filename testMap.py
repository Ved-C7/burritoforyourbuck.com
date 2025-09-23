import re
import json
from opencage.geocoder import OpenCageGeocode

# List of OpenCage API keys
API_KEYS = ['63feef7833ea4353899ee66f48fa43ca', '03cb1ef5c38d4ac5876e4fec7a8bdb90']
current_key_index = 0
request_count = 0
request_limit = 1900

# Function to get a geocoder instance with the current API key
def get_geocoder():
  global current_key_index
  return OpenCageGeocode(API_KEYS[current_key_index])

geocoder = get_geocoder()

# Function to parse the store prices file
def parse_prices(file_path):
  store_prices = {}
  with open(file_path, 'r') as file:
      current_store = None
      for line in file:
          if line.startswith("Store"):
              current_store = line.split()[1][:-1]
              store_prices[current_store] = {}
          elif current_store:
              match = re.match(r'(\S+ - [\w\s]+): \$(\d+\.\d+)', line)
              if match:
                  item, price = match.groups()
                  store_prices[current_store][item] = float(price)
  return store_prices

# Function to parse the store addresses file
def parse_addresses(file_path):
  store_addresses = {}
  with open(file_path, 'r') as file:
      for line in file:
          match = re.match(r'(\d+|Number not found) - (.+)', line)
          if match:
              store_code, address = match.groups()
              if store_code != "Number not found":
                  store_addresses[store_code] = address
  return store_addresses

# Function to geocode addresses
def geocode_address(address):
  global request_count, current_key_index, geocoder
  request_count += 1
  if request_count >= request_limit:
      current_key_index = (current_key_index + 1) % len(API_KEYS)
      geocoder = get_geocoder()
      request_count = 0  # Reset request count after switching keys
      print("Switched!")
  result = geocoder.geocode(address)
  if result and len(result):
      return result[0]['geometry']['lat'], result[0]['geometry']['lng']
  return None, None

# Parse the files
store_prices = parse_prices('DakotaPrices.txt')
store_addresses = parse_addresses('DakNumbers.txt')

# Combine the data and geocode addresses
store_data = []
for store_code, prices in store_prices.items():
  if store_code in store_addresses:
      address = store_addresses[store_code]
      lat, lng = geocode_address(address)
      if lat and lng:
          store_data.append({
              'store_code': store_code,
              'address': address,
              'lat': lat,
              'lng': lng,
              'prices': prices
          })
          #print(address)
      else:
          print(f"Geocoding failed for address: {address}")

# Save the combined data to a JSON file
with open('store_dataDAK.json', 'w') as file:
  json.dump(store_data, file, indent=4)