
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError

from config import upload_file
from .models import db, Product
from flask import request, jsonify, make_response, Blueprint, Flask

from .. import api
from ..users.models import User
from ..utils import create_response
from flask_restx import Resource, Api



class ProductSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    stock_quantity = fields.Int(required=True)
    price = fields.Float(required=True)
    image_url = fields.Str(required=True)

products_bp = Blueprint('products', __name__)


# app = Flask(__name__)
# api = Api(app)

@api.route('/hello')
class HelloWorld(Resource):
    @api.doc('hellokk')
    def post(self):
        return {'hello': 'world'}


@api.route('/upload_image')
class Products(Resource):
    @api.doc('upload_image')

    def post(self):

        try:
            if 'image' not in request.files:
                return jsonify({'message': 'No image file provided'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400

            if file and allowed_file(file.filename):
                image_url = upload_file(file)
                return create_response(data=image_url, message="Success", status=201)

            else:
                return create_response(error="Invalid file type", message="Invalid file type", status=400)

        except Exception as e:

            return create_response(error=str(e), message="An error occurred while adding the image", status=500)


@products_bp.route('/image-upload', methods=['POST'])
def upload_image():
        try:
            if 'image' not in request.files:
                return jsonify({'message': 'No image file provided'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400

            if file and allowed_file(file.filename):
                image_url = upload_file(file)
                return create_response(data=image_url, message="Success", status=201)

            else:
                return create_response(error="Invalid file type", message="Invalid file type", status=400)

        except Exception as e:


            return create_response(error=str(e), message="An error occurred while adding the image", status=500)




@products_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)


        if not user or not user.role:
            return jsonify({
                'message': 'Unauthorized',
                'status': 401
            }), 401

        schema = ProductSchema()

        try:
            data = schema.load(request.get_json())
        except ValidationError as e:
            return jsonify(e.messages), 400


        name =data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock_quantity = data.get('stock_quantity')
        image_url = data.get('image_url')

        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
        except ValueError:
            return create_response(error='Invalid price or stock quantity',  message="Invalid price or stock quantity", status=400)


        product = Product(
            name=name,
            slug=f"{name}-{price}".lower().replace(' ', '-'),
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            product_image=image_url
        )

        db.session.add(product)
        db.session.commit()

        return create_response(data=product, message="Success", status=201)


    except Exception as e:

        return create_response(error=str(e), message="An error occurred while adding product", status=500)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.order_by(Product.created_at).all()

        return create_response(data=products, message="Success", status=200)

    except Exception as e:


        return create_response(error=str(e), message="An error occurred while fetching product", status=500)



@products_bp.route('/products/<string:slug>', methods=['GET'])
def get_product(slug):
    try:

        product = Product.query.filter_by(slug =slug).first()

        if product is None:
            return create_response(error="Product not found", message="Product not found", status=404)

        return create_response(data=product, message="Success", status=200)

    except Exception as e:


        return create_response(error=str(e), message="An error occurred while fetching product", status=500)









