from flask import Flask, request, render_template, send_file
from spotifyBingo import create_bingo_boards

app = Flask(__name__)

def process_url(url, count):
    """
    A placeholder function that processes the URL.
    Replace this with your own implementation.
    """
    # For demonstration, we'll just print the URL.
    # In your real application, you might parse the URL,
    # fetch data, etc.
    count = int(count)
    zips = create_bingo_boards(count, url)
    
    return zips

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the URL from the form input named 'user_url'
        user_url = request.form.get('user_url')
        count = request.form.get('user_number')  # Note: Comes in as a string

        if user_url:
            # Pass the URL to your backend function
            zips = process_url(user_url, count)
            return send_file(zips, mimetype='application/zip', as_attachment=True, download_name='bingo_boards.zip')
        return render_template('index.html', message="URL received!")
    # For a GET request, simply render the homepage with the form
    return render_template('index.html', message="Paste a URL below:")

if __name__ == '__main__':
    app.run(debug=True)
