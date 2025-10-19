import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_youtube_views(driver, track_name, artist_name):
    search_query = f"{track_name} {artist_name}".lower().replace(" ", "+")
    youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
    print(f"Wyszukiwanie: {youtube_search_url}")

    driver.get(youtube_search_url)
    time.sleep(3)
    total_views = 0

    try:
        first_video_views_xpath = "(//ytd-video-renderer//span[@class='inline-metadata-item style-scope ytd-video-meta-block'])[1]"
        first_views_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, first_video_views_xpath))
        )
        first_views_text = first_views_element.text
        print("Tekst pierwszego filmu:", first_views_text)
        first_views_text = first_views_text.replace(" wyświetleń", "")
        first_views_text = first_views_text.replace(",", ".")
        first_views = parse_views(first_views_text)
        print(f"Pierwszy film: {first_views:,}")

        total_views += first_views

        second_video_views_xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer[1]/div[3]/ytd-video-renderer[2]/div[1]/div/div[1]/ytd-video-meta-block/div[1]/div[2]/span[1]"
        second_views_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, second_video_views_xpath))
        )
        second_views_text = second_views_element.text
        print("Tekst wyświetleń drugiego filmu:", second_views_text)
        second_views_text = second_views_text.replace(" wyświetleń", "")
        second_views_text = second_views_text.replace(",", ".")
        second_views = parse_views(second_views_text)
        print(f"Drugi film: {second_views:,}")

        total_views += second_views

    except Exception as e:
        print("Błąd:", e)

    return total_views

def parse_views(views_text):
    try:
        print("Parsowanie tekstu:", views_text)
        views_text = views_text.replace(" ", "").lower()

        if "mld" in views_text:
            number = float(views_text.replace("mld", ""))
            return int(number * 1_000_000_000)  # Miliardy
        elif "mln" in views_text:
            number = float(views_text.replace("mln", ""))
            return int(number * 1_000_000)  # Miliony
        elif "tys" in views_text:
            number = float(views_text.replace("tys", ""))
            return int(number * 1_000)  # Tysiące
        else:
            return int(float(views_text))
    except Exception as e:
        print("Błąd parsowania:", e)
        return 0

def format_views_with_zeros(views):
    return f"{views:,}".replace(",", "")
def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        input_file = "all_tracksspotify2_results.xlsx"
        df = pd.read_excel(input_file)

        df['youtube_views'] = 0

        for index, row in df.head(1000).iterrows():
            track_name = row['track.name']
            artist_name = row['track.artist']

            views = get_youtube_views(driver, track_name, artist_name)
            formatted_views = format_views_with_zeros(views)
            df.at[index, 'youtube_views'] = formatted_views

            print(f"Utwór: {track_name} | Artysta: {artist_name} | Wyświetlenia: {formatted_views}")
            time.sleep(2)

        output_file = "all_tracksspotify2_results_final.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Wyniki zapisano do pliku: {output_file}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
