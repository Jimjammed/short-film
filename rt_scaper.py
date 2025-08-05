import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

# -------------------------------
# 🔧 CONFIG
OMDB_API_KEY = "5ae9fc9a"


movie_titles = [
    "Bao",                               
    "Piper",                           
    "Hair Love",                       
    "If Anything Happens I Love You",   
    "The Silent Child",                 
    "World of Tomorrow",                
    "Stutterer",                         
    "Paperman",                          
    "La Luna",                          
    "Kitbull",                         
    "Loop",                           
    "Burrow",                        
    "For the Birds",                     
    "Feast",                             
    "The Present"     
]

# -------------------------------
# 🚗 Setup Chrome Driver
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1200,800")

driver = webdriver.Chrome(options=options)

# -------------------------------
# 📦 Prepare CSV Output
output_file = open("combined_movie_data.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(output_file)
csv_writer.writerow(["Title", "Year", "Genre", "BoxOffice", "IMDB Rating", "Tomatometer", "Audience Score", "RT URL"])

# -------------------------------
# 🔁 Loop through movies
for title in movie_titles:
    print(f"\n🎬 Searching: {title}")

    # 1️⃣ Step 1: OMDb API Request
    omdb_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    response = requests.get(omdb_url)
    data = response.json()

    if data.get("Response") == "False":
        print(f"❌ Movie not found in OMDb: {title}")
        continue

    year = data.get("Year", "N/A")
    genre = data.get("Genre", "N/A")
    box_office = data.get("BoxOffice", "N/A")
    imdb_rating = data.get("imdbRating", "N/A")

    # 2️⃣ Step 2: Try building RT link
    rt_url = f"https://www.rottentomatoes.com/m/{title.lower().replace(' ', '_')}"
    driver.get(rt_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "score-board"))
        )
        time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        score_board = soup.select_one("score-board")

        tomato_score = score_board.get("tomatometerscore", "N/A") if score_board else "N/A"
        audience_score = score_board.get("audiencescore", "N/A") if score_board else "N/A"

    except Exception as e:
        print(f"⚠️ Rotten Tomatoes data missing for: {title}")
        tomato_score = "N/A"
        audience_score = "N/A"

    # 3️⃣ Final: Display and Save Combined Results
    print(f"📊 {title} ({year})")
    print(f"🎭 Genre: {genre}")
    print(f"💰 Box Office: {box_office}")
    print(f"⭐ IMDb Rating: {imdb_rating}")
    print(f"🍅 Tomatometer: {tomato_score}%")
    print(f"👥 Audience Score: {audience_score}%")
    print(f"🔗 RT URL: {rt_url}")

    csv_writer.writerow([title, year, genre, box_office, imdb_rating, tomato_score, audience_score, rt_url])

# -------------------------------
# ✅ Done
print("\n✅ Finished. Data saved to 'combined_movie_data.csv'")
output_file.close()
driver.quit()
