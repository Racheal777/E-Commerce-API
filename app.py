import os

from dotenv import load_dotenv

from src import create_app
# from log_config import logger

load_dotenv()


app = create_app()
app.app_context().push()

if __name__ == "__main__":
    # logger.info('Application starting...')
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
