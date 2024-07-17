import requests
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('en_data.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS user_informations (
    id INTEGER PRIMARY KEY,
    seq INTEGER,
    displayOrder INTEGER,
    informationType TEXT,
    informationTag TEXT,
    browseType TEXT,
    platform TEXT,
    title TEXT,
    path TEXT,
    startAt INTEGER,
    endAt INTEGER,
    bannerAssetbundleName TEXT,
    messageSent INTEGER DEFAULT 0
)
''')
conn.commit()

# Function to fetch and save the JSON data to the database
def fetch_and_save_json_to_en_db(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    json_data = response.json()

    # Insert new data into the table if the id does not already exist
    for info in json_data:
        id_val = info.get('id')

        # Check if id exists in the database
        c.execute('SELECT id FROM user_informations WHERE id = ?', (id_val,))
        existing_id = c.fetchone()

        if not existing_id:
            # Insert new record if id does not exist
            seq_val = info.get('seq')
            display_order_val = info.get('displayOrder')
            info_type_val = info.get('informationType')
            info_tag_val = info.get('informationTag')
            browse_type_val = info.get('browseType')
            platform_val = info.get('platform')
            title_val = info.get('title')
            path_val = info.get('path')
            start_at_val = info.get('startAt')
            end_at_val = info.get('endAt', None)
            banner_val = info.get('bannerAssetbundleName', None)

            # Insert with messageSent set to False (0)
            c.execute('''
            INSERT INTO user_informations 
            (id, seq, displayOrder, informationType, informationTag, browseType, platform, title, path, startAt, endAt, bannerAssetbundleName, messageSent) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (id_val, seq_val, display_order_val, info_type_val, info_tag_val, browse_type_val, platform_val, title_val, path_val, start_at_val, end_at_val, banner_val, 0))
            print(f"Inserted new data: {info}")

    conn.commit()
    print("Committed changes to database")

    return True  # Optionally return a success flag or data count

# Function to update messageSent flag in the database
def update_en_message_sent(id):
    c.execute('UPDATE user_informations SET messageSent = 1 WHERE id = ?', (id,))
    conn.commit()

# Function to retrieve entries for processing
def get_en_entries_to_process():
    current_time = int(datetime.now().timestamp() * 1000)
    c.execute('''
        SELECT id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName
        FROM user_informations
        WHERE messagesent = 0 AND (endAt IS NULL OR ? <= endAt)
    ''', (current_time,))
    return c.fetchall()
