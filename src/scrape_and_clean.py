import lyricsgenius
from bs4 import BeautifulSoup
from urllib import request
import nltk
import requests
import pandas as pd
from typing import List
import re
from nltk.corpus import words

# Set up Genius API with your token
genius = lyricsgenius.Genius("your_genius_token", timeout=15)

def get_lyrics_from_genius(row):
    try:
        song = genius.search_song(row['track_name'], row['artists'])
        return song.lyrics if song else "Lyrics not found"
    except Exception as e:
        print(f"Error occurred while fetching lyrics: {e}")
        return "Lyrics not found"

def clean_lyrics(lyrics):
    # Remove bracketed text and any preamble text up to the first closing bracket
    lyrics = re.sub(r'^.*?\]', '', lyrics, flags=re.DOTALL)  # Removes from start of lyrics to first ']'
    lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Removes any remaining bracketed sections
    # Remove trailing 'Embed' and any numbers directly before it
    lyrics = re.sub(r'\d*Embed$', '', lyrics, flags=re.MULTILINE)
    return lyrics.strip()  # Remove any leading/trailing whitespace

def is_english(lyrics):
    # Simple heuristic: If the number of ASCII characters is below a certain threshold, consider it non-English
     # Load list of English words
    english_vocab = set(words.words())
    words_in_lyrics = set(nltk.word_tokenize(lyrics.lower()))  # Tokenize and convert to lower case
    english_words = words_in_lyrics.intersection(english_vocab)
    
    if len(words_in_lyrics) == 0:  # Prevent division by zero
        return False

def create_genre_df(genres: List[str], sample: int, spotifydf: pd.DataFrame):
    frames = []
    for genre in genres:
        genre_df = spotifydf[spotifydf['track_genre'] == genre].copy()
        lyrics_df = pd.DataFrame(columns=spotifydf.columns)  # Ensure we have the same columns
        
        while len(lyrics_df) < sample and not genre_df.empty:
            sample_df = genre_df.sample(n=1)
            sample_df['Lyrics'] = sample_df.apply(get_lyrics_from_genius, axis=1)
            sample_df['Lyrics'] = sample_df['Lyrics'].apply(clean_lyrics)
            
            # Only append if lyrics were found and the song is in English
            if sample_df['Lyrics'].iloc[0] != "Lyrics not found" and is_english(sample_df['Lyrics'].iloc[0]):
                lyrics_df = pd.concat([lyrics_df, sample_df])
                
            # Remove sampled row from genre_df to avoid resampling
            genre_df = genre_df.drop(sample_df.index)
        
        frames.append(lyrics_df)
        
    return pd.concat(frames, ignore_index=True)