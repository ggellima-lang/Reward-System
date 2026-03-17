import requests
from bs4 import BeautifulSoup

# 1. The URL you want to scrape
url = "https://builtbybit.com/resources/altar-smp-legendries-arc-5.89897/"

# 2. Download the page content
response = requests.get(url)

# 3. Check if the page loaded correctly
if response.status_code == 200:
    # 4. Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 5. Find specific data (e.g., all <h1> tags)
    headings = soup.find_all('h1')
    
    for h in headings:
        print(h.text)
else:
    print(f"Failed to reach site. Error code: {response.status_code}")