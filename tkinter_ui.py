import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

# Load environment variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Spotify authentication manager
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="https://example.com/callback/",
    scope="playlist-modify-private",
    cache_path=".spotipyoauthcache",
    show_dialog=True,
)

# Create the main window
window = tk.Tk()
window.title("Spotify Time Capsule")
window.config(padx=20, pady=20)

# Create a calendar to pick a date
calendar = Calendar(window, selectmode="day", year=2024, month=1, day=1,
                    font=('Arial', 16), foreground='black', title_font=('Arial', 16, 'bold'), showweeknumbers=False)

# Create a label asking to pick a date
date_label = tk.Label(window, text="Pick a date and we'll create a top 100 playlist from that year! ")

# Spotify authentication manager
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="https://example.com/callback/",
    scope="playlist-modify-private",
    cache_path=".spotipyoauthcache",
    show_dialog=True,
)

# Create a new Spotify object with the obtained token_info
token_info = sp_oauth.get_cached_token()

# If token is not available or expired, use refresh token
if not token_info or sp_oauth.is_token_expired(token_info):
    token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

# Create a new Spotify object with the obtained token_info
sp = spotipy.Spotify(auth=token_info['access_token'])

# Get the user ID using the authentication manager
user_id = sp.current_user()["id"]

# Create a button to trigger the playlist function
def make_playlist():
    # Function to make a playlist
    selected_date_str = calendar.get_date()
    selected_date = datetime.datetime.strptime(selected_date_str, "%m/%d/%y").date()
    year = selected_date.year
    month = selected_date.month
    day = selected_date.day

    # Construct the Billboard Hot 100 URL
    billboard_url = f"https://www.billboard.com/charts/hot-100/{year}-{month:02d}-{day:02d}"

    # Fetch data from the Billboard website
    response = requests.get(billboard_url)

    # Prettify and print the response content
    soup = BeautifulSoup(response.text, "html.parser")
    song_names_spans = soup.select("li ul li h3")
    song_names = [song.getText().strip() for song in song_names_spans]

    # Update the label with song names
    songs_display.config(text="\n".join(" | ".join(song_names[i:i+5]) for i in range(0, len(song_names), 5)))


    # Update the window
    window.update_idletasks()

    # Ask the user if they want to create the playlist
    user_response = tk.messagebox.askquestion("Create Playlist", "Do you want to create a playlist on Spotify?")

    if user_response == 'yes':
        # Search Spotify for songs by title
        song_uris = []
        skipped_songs = []

        for song in song_names:
            result = sp.search(q=f"track:{song} year:{year}", type="track")

            # Try to get the first URI
            try:
                uri = result["tracks"]["items"][0]["uri"]
                song_uris.append(uri)
            except IndexError:
                skipped_songs.append(song)
        if skipped_songs:
            skipped_songs_string = "\n".join(skipped_songs)
            tk.messagebox.showinfo("Skipped Songs", f"The following songs were skipped as they don't exist in Spotify: \n{skipped_songs_string}")

        # Create a new playlist
        playlist = sp.user_playlist_create(user=user_id, name=f"{year}-{month:02d}-{day:02d} Billboard 100", public=False)

        # Adding songs found into the new playlist
        sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

        # Update the label with playlist details
        playlist_info = f"Playlist created for {year}-{month:02d}-{day:02d}.\nPlaylist ID: {playlist['id']}"
        songs_display.config(text=playlist_info)
    else:
        songs_display.config(text="Ok, pick a new year.")

# Button to trigger the playlist function
button = tk.Button(window, text="Travel Now", command=make_playlist)

# Create a label to display the top 100 songs
songs_label = tk.Label(window, text="Top 100 Songs:")

# Create a label to display the songs in 5 columns with 20 rows
songs_display = tk.Label(window, justify='center', font=('Arial', 10))

# grids
calendar.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
date_label.grid(row=1, column=1, columnspan=1, padx=10, pady=10, sticky='nsew')
button.grid(row=3, column=1, columnspan=1, padx=10, pady=10, sticky='nsew')
songs_label.grid(row=4, column=1, columnspan=1, padx=10, pady=10, sticky='nsew')
songs_display.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Start the main loop
window.mainloop()
