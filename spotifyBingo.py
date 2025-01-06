import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import textwrap
import requests
import io
import zipfile
from dotenv import load_dotenv
import os

load_dotenv()

secret = os.getenv("SECRET_ID")

def get_bearer_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("SECRET_ID"),
        "client_secret": os.getenv("SECRET_SECRET"),
    }

    response = requests.post(url, headers=headers, data=data)

    access_token = response.json()["access_token"]

    return access_token

def get_playlist_id(url):
    tag = url.split('/')[-1]
    playlist_id = tag.split('?')[0]
    return playlist_id

def get_playlist_tracks(url):
    playlist_id = get_playlist_id(url)
    token = get_bearer_token()
    hasNext = True
    i = 0
    songList = []
    while hasNext != False:
        response = get_track_page(playlist_id, token, i)
        songs = response['items']
        for j in range(len(songs)):
            name = songs[j]['track']['name']
            artist = songs[j]['track']['artists'][0]['name']
            songList.append((name, artist))
        if response['next'] == None:
            hasNext = False
        else:
            i += 1
    return songList

def get_track_page(playlist_id, token, page):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    params = {
        "limit": '20',
        "offset": f"{page * 20}"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# Generate a bingo board with 24 random songs and a free space in the center
def generate_bingo_board(songs):
    selected_songs = random.sample(songs, 24)
    bingo_board = selected_songs[:12] + ['Free Space'] + selected_songs[12:]
    return [bingo_board[i*5:(i+1)*5] for i in range(5)]

# Create and save the bingo board as a PDF
def create_bingo_pdf(bingo_board):
    pdf_stream = io.BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=letter)
    width, height = letter

    # Set up constants for layout
    margin = 50
    cell_size = (width - 2 * margin) / 5
    x_offset, y_offset = margin, height - margin - cell_size
    
    # Draw the bingo board grid and fill in songs
    for i in range(5):
        for j in range(5):
            x = x_offset + j * cell_size
            y = y_offset - i * cell_size
            
            # Draw cell border
            c.setStrokeColor(colors.black)
            c.rect(x, y, cell_size, cell_size)
            
            # Set text
            song = bingo_board[i][j]
            wrapped_text = textwrap.wrap(song, width=15)  # wrap text to a max of 15 characters per line
            text_x, text_y = x + cell_size / 2, y + cell_size / 2
            
            # Draw each line of the wrapped text
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for line_index, line in enumerate(wrapped_text):
                line_height = text_y + (len(wrapped_text) - 1) * 6 / 2 - line_index * 12
                c.drawCentredString(text_x, line_height, line)

    # Add Bingo title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - margin / 2, "Spotify Bingo")

    # Save PDF
    c.save()
    pdf_stream.seek(0)  # Move to the start of the stream for reading
    return pdf_stream

# Main function to generate 30 bingo board PDFs
def create_bingo_boards(count, url):
    info = get_playlist_tracks(url)
    if len(info) < 24:
        raise ValueError("The playlist must contain at least 24 songs to generate a bingo board.")

    # Merge (song, artist) into a single string
    songs = [f"{song} - {artist}" for song, artist in info]

    # Truncate each to 75 characters
    songs = [song[:75] for song in songs]
    
    files = []

    zip_stream = io.BytesIO()

    with zipfile.ZipFile(zip_stream, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for _ in range(count):
            bingo_board = generate_bingo_board(songs)
            file = create_bingo_pdf(bingo_board)
            zf.writestr(f"spotify_bingo_{_ + 1}.pdf", file.getvalue())
    
    zip_stream.seek(0)
    
    return zip_stream