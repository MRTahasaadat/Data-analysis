import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.mehrnews.com/service/Economy"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    p_tags = soup.find_all('p')

    p_texts = [p.get_text(strip=True) for p in p_tags]

    df = pd.DataFrame(p_texts, columns=['Paragraph Text'])

    df.to_csv('paragraphs.csv', index=False, encoding='utf-8')

    print("Data has been saved to paragraphs.csv")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
