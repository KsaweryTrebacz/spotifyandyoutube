from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

data_file_path = 'all_tracksspotify2.xlsx'
data = pd.read_excel(data_file_path)

if 'track.name' not in data.columns:
    raise ValueError("Kolumna 'track.name' nie istnieje w pliku Excel.")

if 'BPM' not in data.columns:
    data['BPM'] = None

batch_size = 1
start_index = 933

track_names = data['track.name'].dropna().tolist()[start_index:]

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--start-maximized')

def restart_driver():
    global driver
    if 'driver' in globals():
        print("Zamykam przeglądarkę przed restartem...")
        driver.quit()
    driver = webdriver.Chrome(options=options)
    driver.get("https://songbpm.com")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/button[2]"))
    ).click()

restart_driver()

try:
    for batch_start in range(0, len(track_names), batch_size):
        batch_end = batch_start + batch_size
        batch_tracks = track_names[batch_start:batch_end]

        if batch_start % 10 == 0 and batch_start > 0:
            print(f"Restart przeglądarki po przetworzeniu {batch_start} utworów.")
            restart_driver()

        for index, track_name in enumerate(batch_tracks, start=start_index + batch_start):
            if pd.notna(data.at[index, 'BPM']):
                print(f"Utwór: {track_name} już ma BPM: {data.at[index, 'BPM']}, pomijanie...")
                continue

            try:
                search_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
                )

                search_field.clear()
                search_field.send_keys(track_name)
                search_field.send_keys(Keys.RETURN)

                bpm_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/a/div[2]/div[3]/span[2]"))
                )

                bpm_value = bpm_element.text
                print(f"Utwór: {track_name}, BPM: {bpm_value}")

                data.at[index, 'BPM'] = bpm_value

            except Exception as e:
                print(f"Nie udało się znaleźć BPM dla utworu: {track_name}. Błąd: {e}")

            time.sleep(random.uniform(2, 5))

        data.to_excel(data_file_path, index=False)

finally:
    print("Zamykanie przeglądarki i zapisywanie danych...")
    data.to_excel(data_file_path, index=False)
    driver.quit()
