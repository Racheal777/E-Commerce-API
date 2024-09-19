import os

from dotenv import load_dotenv

from src import app

load_dotenv()


import mailings

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
