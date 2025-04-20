import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the website to scrape
url = "https://www.mehrnews.com/service/Economy"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <p> tags
    p_tags = soup.find_all('p')

    # Extract text from each <p> tag
    p_texts = [p.get_text(strip=True) for p in p_tags]

    # Create a DataFrame from the list of texts
    df = pd.DataFrame(p_texts, columns=['Paragraph Text'])

    # Save the DataFrame to a CSV file
    df.to_csv('paragraphs.csv', index=False, encoding='utf-8')

    print("Data has been saved to paragraphs.csv")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")