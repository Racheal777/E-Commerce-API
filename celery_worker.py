# celery_worker.py
from src import create_app
from src.task import celery

app = create_app()
app.app_context().push()