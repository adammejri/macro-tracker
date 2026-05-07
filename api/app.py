from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from api.routes.nutrition import nutrition_bp
    from api.routes.meals import meals_bp
    from api.routes.activities import activities_bp
    from api.routes.summary import summary_bp

    app.register_blueprint(nutrition_bp, url_prefix="/api/nutrition")
    app.register_blueprint(meals_bp,     url_prefix="/api/meals")
    app.register_blueprint(activities_bp, url_prefix="/api/activities")
    app.register_blueprint(summary_bp,   url_prefix="/api/summary")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)