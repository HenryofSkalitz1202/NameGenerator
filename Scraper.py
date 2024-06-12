import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import errorcode
import time

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'names',
}

# URL of the website to scrape
BASE_URL = 'https://www.momjunction.com/baby-names'

# Connect to MySQL database
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Create a table to store names and their meanings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS names (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        gender ENUM('Girl', 'Unisex', 'Boy'),
        meaning TEXT
    )
    ''')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit()

def scrape_names(base_url, names_page):
    """
    Scrape names and their meanings from the website and store them in the database.
    """
    response = requests.get(base_url + names_page)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    meaning = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="from_functions")
    for row in meaning.tbody.find_all('tr'):
        col = row.find_all('td')
        
        if(len(col) < 3):
            continue
        
        name = col[0].text.strip()
        gender = col[2].text.strip()
        meaning = col[3].text.strip()
        
        # Insert the name, gender, meaning into the database
        cursor.execute('INSERT INTO names (name, gender, meaning) VALUES (%s, %s, %s)', (name, gender, meaning))
        print(f'Scraped and stored: {name} - {gender} - {meaning}')
        
    # Commit the transaction
    conn.commit()

# Run the scraper
for i in range(50, 60):
    NAMES_PAGE = '/boy/starting-with-a/page/' + str(i)
    scrape_names(BASE_URL, NAMES_PAGE)
    time.sleep(5)

# Close the database connection
cursor.close()
conn.close()
