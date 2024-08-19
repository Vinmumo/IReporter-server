from flask import Flask, jsonify
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from .extensions import db, migrate
from config import Config

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


    db.init_app(app)
    migrate.init_app(app, db)
    
    jwt = JWTManager(app)
    jwt.init_app(app)

    mail.init_app(app)  # Initialize Flask-Mail

    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid JWT token',
            'message': str(error)
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(error):
        return jsonify({
            'error': 'Expired JWT token',
            'message': str(error)
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': str(error)
        }), 401

    @jwt.needs_fresh_token_loader
    def fresh_token_required_callback(error):
        return jsonify({
            'error': 'Fresh token required',
            'message': str(error)
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(error):
        return jsonify({
            'error': 'Token has been revoked',
            'message': str(error)
        }), 401
    
    api = Api(app,
              version='1.0',
              title='iReporter API',
              description='A comprehensive API for the iReporter platform, enabling citizens to report corruption and request government intervention.',
              doc='/api/docs',
              authorizations={
                  'apikey': {
                      'type': 'apiKey',
                      'in': 'header',
                      'name': 'Authorization'
                  }
              },
              security='apikey',
              license='MIT',
              license_url='https://opensource.org/licenses/MIT',
              contact='API Support',
              contact_url='http://www.ireporter.com/support',
              contact_email='info@ireporter.com',
              default='iReporter',
              default_label='iReporter operations'
    )
    
    from .routes.auth_routes import api as auth_ns
    from .routes.record_routes import api as record_ns
    from .routes.image_routes import api as image_ns
    from .routes.video_routes import api as video_ns

    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(record_ns, path='/api/records')
    api.add_namespace(image_ns, path='/api/images')
    api.add_namespace(video_ns, path='/api/videos')

    with app.app_context():
        db.create_all()

    return app
