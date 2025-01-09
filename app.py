from flask import Flask, request, render_template, send_file
from spotifyBingo import create_bingo_boards

app = Flask(__name__)

def process_url(url, count, title, size, include_free):
    """
    A placeholder function that processes the URL.
    Replace this with your own implementation.
    """
    # For demonstration, we'll just print the URL.
    # In your real application, you might parse the URL,
    # fetch data, etc.
    zips = create_bingo_boards(count, url, title, size, include_free)
    
    return zips

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the URL from the form input named 'user_url'
        user_url = request.form.get('user_url')
        count = request.form.get('user_number')  # Note: Comes in as a string
        title = request.form.get('title')  # Note: Comes in as a string
        size = request.form.get('board_size')
        free_space = request.form.get('include_free')
        include_free = (free_space == 'on')
        size = int(size)
        count = int(count)
        if title == "":
            title = "Spotify Bingo"
        if user_url:
            # Pass the URL to your backend function
            zips = process_url(user_url, count, title, size, include_free)
            return send_file(zips, mimetype='application/zip', as_attachment=True, download_name='bingo_boards.zip')
        return render_template('index.html', message="Your Bingo Boards have been generated!")
    # For a GET request, simply render the homepage with the form
    return render_template('index.html', message="Convert your Spotify playlist into Bingo Boards!")

if __name__ == '__main__':
    app.run(debug=True)
