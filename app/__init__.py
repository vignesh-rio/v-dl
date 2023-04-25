from flask import Flask

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config')

# Import and register routes
from app import routes

# Import and register form
from app.forms import DownloadForm
app.jinja_env.globals.update(download_form=DownloadForm())
