import os

from dotenv import load_dotenv

from src import app

load_dotenv()




if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
