from myapp import create_app
from myapp.routes.auth_routes import auth_bp

app = create_app()

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)