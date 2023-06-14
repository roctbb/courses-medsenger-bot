from manage import *
from helpers import *
from blueprints.editor import editor_blueprint
from blueprints.medsenger import medsenger_blueprint

app.register_blueprint(editor_blueprint, url_prefix='/editor')
app.register_blueprint(medsenger_blueprint, url_prefix='')


@app.route('/')
def index():
    return "Waiting for the thunder"


if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
