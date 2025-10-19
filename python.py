from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

def get_play_count(artist_id, track_name):
    url = f"https://kworb.net/spotify/artist/{artist_id}_songs.html"
    driver.get(url)

    try:
        table_xpath = "/html/body/div[1]/div[5]/table[2]/tbody"

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, table_xpath)))

        rows = driver.find_elements(By.XPATH, f"{table_xpath}/tr")

        for row in rows:
            track_name_element = row.find_element(By.XPATH, "./td[1]/div/a")
            track_name_in_table = track_name_element.text

            if track_name_in_table == track_name:
                play_count_element = row.find_element(By.XPATH, "./td[2]")
                play_count = play_count_element.text
                print(f"Track: {track_name_in_table} | Play count: {play_count}")
                return play_count

        print(f"Track '{track_name}' not found.")
        return None

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error for track '{track_name}' (Artist ID: {artist_id}): {e}")
    except Exception as e:
        print(f"Unexpected error for track '{track_name}' (Artist ID: {artist_id}): {e}")

    return None

file_path = 'all_tracksspotify2.xlsx'
data = pd.read_excel(file_path)

if 'track.artist.id' not in data.columns or 'track.name' not in data.columns:
    raise ValueError("Plik musi zawierać kolumny 'track.artist.id' oraz 'track.name'.")

artist_ids = data['track.artist.id'].dropna().tolist()
track_names = data['track.name'].dropna().tolist()

play_counts = []

for artist_id, track_name in zip(artist_ids, track_names):
    print(f"Processing Artist ID: {artist_id}, Track Name: {track_name}")
    play_count = get_play_count(artist_id, track_name)
    play_counts.append(play_count)
    time.sleep(2)

data['play_count'] = play_counts

output_file = 'all_tracksspotify2_results.xlsx'
data.to_excel(output_file, index=False)
print(f"Scraping completed. Results saved to {output_file}.")

driver.quit()

