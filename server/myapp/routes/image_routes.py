from flask import Blueprint, request, jsonify
from ..models.image import Image, db
from ..services.cloudinary_services import upload_file


image_bp = Blueprint('image_bp', __name__)

# Get all images
@image_bp.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([image.to_dict() for image in images]), 200

# Get images by record_id
@image_bp.route('/records/<int:record_id>/images', methods=['GET'])
def get_images_by_record(record_id):
    images = Image.query.filter_by(record_id=record_id).all()
    return jsonify([image.to_dict() for image in images]), 200

# Upload a new image
@image_bp.route('/records/<int:record_id>/images', methods=['POST'])
def upload_image(record_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    upload_result = upload_file(file)
    image = Image(url=upload_result['url'], record_id=record_id)
    db.session.add(image)
    db.session.commit()
    return jsonify({'message': 'Image uploaded successfully', 'url': upload_result['url']}), 201

# Delete an image by ID
@image_bp.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404

    db.session.delete(image)
    db.session.commit()
    return jsonify({'message': 'Image deleted successfully'}), 200

