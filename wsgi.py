# ENTRY POINT
# Initialises main flask app

from flask import Flask

def flask_app():
    app = Flask(__name__, instance_relative_config=False)
    #app.config.from_object('config.Config')

    with app.app_context():
        # Core flask app pages
        import routes as routes

        # Import Dash app
        from dashboard import init_dashboard
        app = init_dashboard(app)

        return app

# Initialise new flask app object
app = flask_app()

# Run server
if __name__ == "__main__":
    app.run(debug=True)