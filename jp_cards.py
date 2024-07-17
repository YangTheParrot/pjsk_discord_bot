import requests
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('jp_data.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    seq INTEGER,
    characterId INTEGER,
    cardRarityType TEXT,
    attr TEXT,
    supportUnit TEXT,
    skillId INTEGER,
    cardSkillName TEXT,
    prefix TEXT,
    assetbundleName TEXT,
    releaseAt INTEGER,
    archivePublishedAt INTEGER,
    messageSent INTEGER DEFAULT 0
)
''')
conn.commit()

# Function to fetch and save the JSON data to the database
def fetch_and_save_cards_to_jp_db(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    json_data = response.json()

    # Insert new data into the table if the id does not already exist
    for card in json_data:
        id_val = card.get('id')

        # Check if id exists in the database
        c.execute('SELECT id FROM cards WHERE id = ?', (id_val,))
        existing_id = c.fetchone()

        if not existing_id:
            # Insert new record if id does not exist
            seq_val = card.get('seq')
            character_id_val = card.get('characterId')
            card_rarity_type_val = card.get('cardRarityType')
            attr_val = card.get('attr')
            support_unit_val = card.get('supportUnit')
            skill_id_val = card.get('skillId')
            card_skill_name_val = card.get('cardSkillName')
            prefix_val = card.get('prefix')
            assetbundle_name_val = card.get('assetbundleName')
            release_at_val = card.get('releaseAt')
            archive_published_at_val = card.get('archivePublishedAt')

            # Insert with messageSent set to False (0)
            c.execute('''
            INSERT INTO cards 
            (id, seq, characterId, cardRarityType, attr, supportUnit, skillId, cardSkillName, prefix, assetbundleName, releaseAt, archivePublishedAt, messageSent) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (id_val, seq_val, character_id_val, card_rarity_type_val, attr_val, support_unit_val, skill_id_val, card_skill_name_val, prefix_val, assetbundle_name_val, release_at_val, archive_published_at_val, 0))
            print(f"Inserted new card: {card}")

    conn.commit()
    print("Committed changes to JP cards database")

    return True  # Optionally return a success flag or data count

# Function to update messageSent flag in the database
def update_jp_cards_message_sent(id):
    c.execute('UPDATE cards SET messageSent = 1 WHERE id = ?', (id,))
    conn.commit()

# Function to retrieve entries for processing
def get_jp_cards_entries_to_process():
    current_time = int(datetime.now().timestamp() * 1000 - 1000000000)
    print(current_time)
    c.execute('''
        SELECT id, characterId, cardRarityType, attr, supportUnit, skillId, cardSkillName, prefix, assetbundleName, releaseAt
        FROM cards
        WHERE messageSent = 0 AND (releaseAt >= ?)
    ''', (current_time,))
    return c.fetchall()
