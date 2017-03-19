from flask import Flask

## contains config variables
import config
import models
from resources.courses import courses_api
from resources.reviews import reviews_api

app = Flask(__name__)
## urls are hardcoded
app.register_blueprint(courses_api)
## has url prefix
app.register_blueprint(reviews_api, url_prefix="/api/v1")

@app.route("/")
def hello_world():
    return "Hello world"

if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=config.PORT, host=config.HOST)
    models.initialize()
