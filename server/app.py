from myapp import create_app
from myapp.routes.auth_routes import auth_bp
from myapp.routes.image_routes import image_bp
from myapp.routes.record_routes import record_bp
from myapp.routes.video_routes import video_bp

app = create_app()

app.register_blueprint(auth_bp)
app.register_blueprint(image_bp)
app.register_blueprint(record_bp)
app.register_blueprint(video_bp)



if __name__ == '__main__':
    app.run(debug=True)