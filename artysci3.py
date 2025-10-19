import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_youtube_subscribers(driver, artist_name, max_retries=3):
    search_query = artist_name.lower().replace(" ", "+")
    youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
    print(f"Wyszukiwanie: {youtube_search_url}")

    retries = 0

    while retries < max_retries:
        try:
            driver.get(youtube_search_url)
            time.sleep(3)

            for i in range(1, 4):
                print(f"Sprawdzanie filmu #{i}")
                video_xpath = f"(//ytd-video-renderer)[{i}]//a[@id='thumbnail']"
                video_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, video_xpath))
                )
                driver.execute_script("arguments[0].click();", video_element)
                time.sleep(3)

                channel_name_xpath = "//ytd-video-owner-renderer//yt-formatted-string[@id='text']/a"
                channel_name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, channel_name_xpath))
                )
                driver.execute_script("arguments[0].click();", channel_name_element)
                time.sleep(3)

                subscribers_xpath = "//yt-content-metadata-view-model/div[2]/span[1]"
                subscribers_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, subscribers_xpath))
                )
                subscribers_text = subscribers_element.text.strip()

                subscribers_text = subscribers_text.replace(" subskrybentów", "").replace("subskrybenci", "").strip()

                print(f"Liczba subskrypcji dla {artist_name}: {subscribers_text}")
                return subscribers_text

            print(f"Nie znaleziono danych dla {artist_name} w próbie #{retries + 1}. Próba ponownie...")
            retries += 1
            time.sleep(5)

        except Exception as e:
            print(f"Błąd podczas przetwarzania dla {artist_name} w próbie #{retries + 1}: {e}")
            retries += 1
            time.sleep(5)

    print(f"Po {max_retries} próbach, nie udało się pobrać danych dla {artist_name}.")
    return "Brak danych"


def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        input_file = "id_counts_df.xlsx"
        df = pd.read_excel(input_file)

        df['youtube_subscribers'] = ""

        for index, row in df.iterrows():
            artist_name = row['artist_name']
            subscribers = get_youtube_subscribers(driver, artist_name)
            df.at[index, 'youtube_subscribers'] = subscribers

            print(f"Artysta: {artist_name} | Subskrypcje: {subscribers}")
            time.sleep(2)
        output_file = "id_counts_df_with_subscribers.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Wyniki zapisano do pliku: {output_file}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
