from imessage_reader import fetch_data
import os
from datetime import date
import re
import pandas as pd


DB_PATH = "/Users/andrewzhang/Library/Messages/chat.db"
IDS = {
    "+17608222626": "al",
    "+15014756934": "zay",
    "+15022037007": "dn",
    "+19175360320": "dz"
}

def convert_to_seconds(time_str):
    # Split the time string into minutes and seconds
    minutes, seconds = time_str.split(':')
    
    # Convert minutes and seconds to integers
    minutes = int(minutes)
    seconds = int(seconds)
    
    # Calculate the total seconds
    total_seconds = minutes * 60 + seconds
    
    return total_seconds

def check_and_handle_games(message, user, date, wordle_df, mini_df, bandle_df):
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

def create_directory_and_csv_files(current_date, wordle_df, mini_df, bandle_df):
    # Create a new directory based on the current date
    directory_name = current_date.strftime("%Y-%m-%d")
    os.makedirs(directory_name, exist_ok=True)
    
    # Write the DataFrames to CSV files in the new directory
    wordle_df.to_csv(os.path.join(directory_name, 'wordle.csv'), index=False)
    mini_df.to_csv(os.path.join(directory_name, 'mini.csv'), index=False)
    bandle_df.to_csv(os.path.join(directory_name, 'bandle.csv'), index=False)
    
    print(f"CSV files created in directory: {directory_name}")            

if __name__ == "__main__":
    fd = fetch_data.FetchData(db_path=DB_PATH)
    messages = fd.get_messages()

    wordle_df = pd.DataFrame(columns=['name', 'score', 'day'])
    mini_df = pd.DataFrame(columns=['name', 'score', 'day'])
    bandle_df = pd.DataFrame(columns=['name', 'score', 'day'])

    current_date = date.today()

    for message in messages:
        user, text, day, _, _, is_me  = message
        if user in IDS: # and (date[:10] == current_date):
            check_and_handle_games(text, user, day, wordle_df, mini_df, bandle_df)
        if is_me or "0320" in user:
            check_and_handle_games(text, "+19175360320", day, wordle_df, mini_df, bandle_df)

    create_directory_and_csv_files(current_date, wordle_df, mini_df, bandle_df)
    
    
