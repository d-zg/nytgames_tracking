from imessage_reader import fetch_data
import os
from datetime import date
import re
import pandas as pd
import gspread
from  oauth2client.service_account import ServiceAccountCredentials

DB_PATH = "/Users/andrewzhang/Library/Messages/chat.db"
IDS = {
    "+17608222626": "al",
    "+15014756934": "zay",
    "+15022037007": "dn",
    "+19175360320": "dz"
}

fd = fetch_data.FetchData(db_path=DB_PATH)
messages = fd.get_messages()

wordle_df = pd.DataFrame(columns=['name', 'score', 'day'])
mini_df = pd.DataFrame(columns=['name', 'score', 'day'])
bandle_df = pd.DataFrame(columns=['name', 'score', 'day'])

current_date = date.today()

def write_to_google_sheet(df, sheet_key, sheet_name):
    # Authenticate and access the Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/credentials.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open_by_key(sheet_key).worksheet(sheet_name)

    # Clear the existing content of the sheet
    sheet.clear()

    # Write the DataFrame to the sheet
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    print(f"DataFrame successfully written to Google Sheet: {sheet_name}")

def convert_to_seconds(time_str):
    # Split the time string into minutes and seconds
    minutes, seconds = time_str.split(':')
    
    # Convert minutes and seconds to integers
    minutes = int(minutes)
    seconds = int(seconds)
    
    # Calculate the total seconds
    total_seconds = minutes * 60 + seconds
    
    return total_seconds

def check_and_handle_games(message, user, date):
    name = IDS[user]
    day = date[:10]
    if not message:
        return

    if "Wordle 1," in message:
        match = re.search(r'(\d+)/6', message)
        if match:
            score = int(match.group(1))
            wordle_df.loc[len(wordle_df)] = [name, score, day]

    elif "New York Times Mini Crossword in" in message:
        try:
            arr = message.split(' ')
            score = arr[-1][:-1]
            score = convert_to_seconds(score)        
            mini_df.loc[len(mini_df)] = [name, score, day]
        except:
            print('bad mini format but continuing')

    elif "Current Streak: " in message:
        try:
            score_str = re.search(r'(\d+)/6', message).group(1)
            score = int(score_str)
            bandle_df.loc[len(bandle_df)] = [name, score, day]
        except AttributeError:
            print("Score not found in the message.")
        except ValueError:
            print("Invalid score format.")
            

for message in messages:
    user, text, date, _, _, is_me  = message
    if user in IDS: # and (date[:10] == current_date):
        check_and_handle_games(text, user, date)
    if is_me or "0320" in user:
        check_and_handle_games(text, "+19175360320", date)


def create_directory_and_csv_files(current_date):
    # Create a new directory based on the current date
    directory_name = current_date.strftime("%Y-%m-%d")
    os.makedirs(directory_name, exist_ok=True)
    
    # Write the DataFrames to CSV files in the new directory
    wordle_df.to_csv(os.path.join(directory_name, 'wordle.csv'), index=False)
    mini_df.to_csv(os.path.join(directory_name, 'mini.csv'), index=False)
    bandle_df.to_csv(os.path.join(directory_name, 'bandle.csv'), index=False)
    
    print(f"CSV files created in directory: {directory_name}")


create_directory_and_csv_files(current_date)
# Assuming you have a DataFrame named 'world_df' and a column named 'name'
counts = wordle_df['name'].value_counts()

# Print the counts
print(counts)
