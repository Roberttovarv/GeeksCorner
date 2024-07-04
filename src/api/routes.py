"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import requests
from flask import Flask, request, jsonify, url_for, Blueprint
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from api.models import db, Users, Games, Carts, CartItems, Products, Orders, OrderItems, Posts, Likes


api = Blueprint('api', __name__)
CORS(api)  


@api.route('/hello', methods=['GET'])
def handle_hello():
    response_body = {}
    response_body["message"] = "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    return response_body, 200

@api.route('/apiexterna', methods=['POST'])
def fetch_and_store_games():
    game_ids = request.json.get('game_ids')
    if not game_ids or not isinstance(game_ids, list):
        return jsonify({'error': 'No hay juegos o el formato es incorrecto'}), 400
    api_key = 'bf752f88a1074c599e4be40330ae959e'
    stored_games = []
    errors = []
    for game_id in game_ids:
        url = f'https://api.rawg.io/api/games/{game_id}?key={api_key}'
        response = requests.get(url)
        if response.status_code != 200:
            errors.append({'game_id': game_id, 'error': 'Fallo al obtener los datos'})
            continue
        game_data = response.json()
        new_game = Games(
            
            name=game_data.get('name'),
            background_image=game_data.get('background_image'),
            description=game_data.get('description')
        )
        db.session.add(new_game)
        stored_games.append(new_game)
    db.session.commit()
    return jsonify({
        'stored_games': [game.serialize() for game in stored_games],
        'errors': errors
    }), 201


@api.route('/users', methods=['GET', 'POST'])  
def handle_users():
    response_body = {}
    if request.method == 'GET':
       
        rows = db.session.execute(db.select(Users)).scalars()
        results = [row.serialize() for row in rows]  
        response_body['results'] = results
        response_body['message'] = 'Listado de Usuarios'
        return response_body, 200
    if request.method == 'POST':
        response_body['message'] = 'Este endpoint no es válido. Ud debe hacer un /signup'
        return response_body, 200
    

@api.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(user_id):
    response_body = {}
    if request.method == 'GET':
        user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
        if user:
            response_body['results'] = user.serialize()
            response_body['message'] = 'Usuario encontrado'
            return response_body, 200
        response_body['message'] = 'Usario inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'PUT':
        data = request.json
        user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
        if user:
            user.email = data['email']
            user.is_active = data['is_active']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.age = data['age']
            user.pfp = data['pfp']
            user.is_admin = data['is_admin']
            db.session.commit()
            response_body['message'] = 'Datos del usuario actualizados'
            response_body['results'] = user.serialize()
            return response_body, 200
        response_body['message'] = 'Usario inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'DELETE':
        user = db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
        if user:
            db.session.delete(user)
            user.is_active = False
            db.session.commit()
            response_body['message'] = 'Usuario eliminado'
            response_body['results'] = {}
            return response_body, 200
        response_body['message'] = 'Usuario inexistente'
        response_body['results'] = {}
        return response_body, 200
    

@api.route('/games', methods=['GET', 'POST'])  
def handle_games():
    response_body = {}
    if request.method == 'GET':
       
        rows = db.session.execute(db.select(Games)).scalars()
        results = [row.serialize() for row in rows]  
        response_body['results'] = results
        response_body['message'] = 'Listado de Videojuegos'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        required_fields = ['name', 'description', 'background_image']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Falta el campo requerido: {field}'}), 400
        row = Games()
        row.name = data['name']
        row.description = data['description']
        row.background_image = data['background_image']
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Videojuego creado'
        return response_body, 201
    

@api.route('/games/<int:game_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_game(game_id):
    response_body = {}
    if request.method == 'GET':
        game = db.session.execute(db.select(Games).where(Games.id == game_id)).scalar()
        if game:
            response_body['results'] = game.serialize()
            response_body['message'] = 'Videojuego encontrado'
            return response_body, 200
        response_body['message'] = 'Videojuego inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'PUT':
        data = request.json
        game = db.session.execute(db.select(Games).where(Games.id == game_id)).scalar()
        if game:
            game.name = data['name']
            game.background_image = data['background_image']
            db.session.commit()
            response_body['message'] = 'Datos del videojuego actualizados'
            response_body['results'] = game.serialize()
            return response_body, 200
        response_body['message'] = 'Videojuego inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'DELETE':
        game = db.session.execute(db.select(Games).where(Games.id == game_id)).scalar()
        if game:
            db.session.delete(game)
            db.session.commit()
            response_body['message'] = 'Videojuego eliminado'
            response_body['results'] = {}
            return response_body, 200
        response_body['message'] = 'Videojuego inexistente'
        response_body['results'] = {}
        return response_body, 404
    

@api.route('/posts', methods=['GET', 'POST'])  # Cambiado
def handle_posts():
    response_body = {}
    if request.method == 'GET':
       
        rows = db.session.execute(db.select(Posts)).scalars()
        results = [row.serialize() for row in rows]  
        response_body['results'] = results
        response_body['message'] = 'Listado de Publicaciones'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        required_fields = ['title', 'body', 'game_id', 'image_url', 'author_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Falta el campo requerido: {field}'}), 400
        row = Posts()
        row.title = data['title']
        row.body = data['body']
        row.image_url = data['image_url']
        row.game_id = data['game_id']
        row.author_id = data['author_id']
        row.date = datetime.today()
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Publicación creada'
        return response_body, 201
    

@api.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_post(post_id):
    response_body = {}
    if request.method == 'GET':
        post = db.session.execute(db.select(Posts).where(Posts.id == post_id)).scalar()
        if post:
            response_body['results'] = post.serialize()
            response_body['message'] = 'Publicación encontrada'
            return response_body, 200
        response_body['message'] = 'Publicación inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'PUT':
        data = request.json
        post = db.session.execute(db.select(Posts).where(Posts.id == post_id)).scalar()
        if post:
            post.title = data['title']
            post.image_url = data['image_url']
            post.body = data['body']
            post.game_id = data['game_id']
            db.session.commit()
            response_body['message'] = 'Publicación actualizada'
            response_body['results'] = post.serialize()
            return response_body, 200
        response_body['message'] = 'Publicación inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'DELETE':
        post = db.session.execute(db.select(Posts).where(Posts.id == post_id)).scalar() 
        if post:
            db.session.delete(post)
            db.session.commit()
            response_body['message'] = 'Publicación eliminada'
            response_body['results'] = {}
            return response_body, 200
        response_body['message'] = 'Publicación inexistente'
        response_body['results'] = {}
        return response_body, 404
    

@api.route('/products', methods=['GET', 'POST'])  
def handle_products():
    response_body = {}
    if request.method == 'GET':
       
        rows = db.session.execute(db.select(Products)).scalars()
        results = [row.serialize() for row in rows]  
        response_body['results'] = results
        response_body['message'] = 'Listado de Productos'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        required_fields = ['cdk', 'game_id', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Falta el campo requerido: {field}'}), 400
        row = Products()
        row.cdk = data['cdk']
        row.game_id = data['game_id']  
        row.price = data['price']
        row.platform = data['platform']
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Producto añadido'
        return response_body, 201
    

@api.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_product(product_id):
    response_body = {}
    if request.method == 'GET':
        product = db.session.execute(db.select(Products).where(Products.id == product_id)).scalar()
        if product:
            response_body['results'] = product.serialize()
            response_body['message'] = 'Producto encontrado'
            return response_body, 200
        response_body['message'] = 'Producto inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'PUT':
        data = request.json
        product = db.session.execute(db.select(Products).where(Products.id == product_id)).scalar()
        if product:
            product.cdk = data['cdk']
            product.game_id = data['game_id'] 
            product.price = data['price']
            db.session.commit()
            response_body['message'] = 'Producto actualizado'
            response_body['results'] = product.serialize()
            return response_body, 200
        response_body['message'] = 'Producto inexistente'
        response_body['results'] = {}
        return response_body, 404
    if request.method == 'DELETE':
        product = db.session.execute(db.select(Products).where(Products.id == product_id)).scalar()
        if product:
            db.session.delete(product)
            db.session.commit()
            response_body['message'] = 'Producto eliminado'
            response_body['results'] = {}
            return response_body, 200
        response_body['message'] = 'Producto inexistente'
        response_body['results'] = {}
        return response_body, 404
    

@api.route('/carts', methods=['GET', 'POST'])  
@jwt_required()
def handle_carts():
    response_body = {}
    current_user = get_jwt_identity()
    print(current_user)
    if request.method == 'GET':
        rows = db.session.execute(db.select(Carts)).scalars()
        results = [row.serialize() for row in rows]  
        response_body['results'] = results
        response_body['message'] = 'Listado de Carritos'
        return response_body, 200
    if request.method == 'POST':
        response_body['message'] = 'Este endpoint no es válido. Ud debe hacer un /signup'
        return response_body, 200
    

@api.route('/carts/<int:cartitem_id>', methods=['GET', 'POST', 'DELETE']) 
def handle_cartitem(cartitem_id):
    response_body = {}
    if request.method == 'GET':
        cartitem = db.session.execute(db.select(CartItems).where(CartItems.id == cartitem_id)).scalar()
        if cartitem:
            response_body['results'] = cartitem.serialize()
            response_body['message'] = 'Productos encontrados'
            return response_body, 200
        response_body['message'] = 'Productos inexistentes'
        response_body['results'] = {}
        return response_body, 404

    if request.method == 'POST':
        data = request.json
        row = CartItems()
        row.product_id = data['product_id']
        row.cart_id = data['cart_id']
        row.quantity = data['quantity']
        db.session.add(row)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Productos añadidos'
        return response_body, 201

    if request.method == 'DELETE':
        cartitem = db.session.execute(db.select(CartItems).where(CartItems.id == cartitem_id)).scalar()
        if cartitem:
            db.session.delete(cartitem)
            db.session.commit()
            response_body['message'] = 'Productos eliminados'
            response_body['results'] = {}
            return response_body, 200
        response_body['message'] = 'Productos inexistentes'
        response_body['results'] = {}
        return response_body, 404


@api.route('/orders', methods=['GET', 'POST'])
def handle_orders():
    response_body = {}
    if request.method == 'GET':
        user_id = request.args.get('user_id')  # Añadido: Obtener user_id de los parámetros de la URL
        if user_id:
            rows = db.session.execute(db.select(Orders).where(Orders.user_id == user_id)).scalars()
        else:
            rows = db.session.execute(db.select(Orders)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de Ordenes'
        return response_body, 200
    if request.method == 'POST':
        data = request.json
        row = Orders()
        row.user_id = data['user_id']
        row.date = datetime.today()
        row.status = 'pendiente de pago'
        # Xra calcular el precio total de la orden
        cart_items = db.session.execute(db.select(CartItems).where(CartItems.cart_id == data['cart_id'])).scalars()
        total_price = sum(item.product_to.price * item.quantity for item in cart_items)
        row.price_total = total_price
        db.session.add(row)
        db.session.commit()
        # Xra crear los OrderItems asociados a la orden
        for item in cart_items:
            order_item = OrderItems(order_id=row.id, product_id=item.product_id, quantity=item.quantity)
            db.session.add(order_item)
        db.session.commit()
        response_body['results'] = row.serialize()
        response_body['message'] = 'Orden creada'
        return response_body, 201


@api.route('/signup', methods=['POST'])
def signup():
    response_body = {}
    data = request.json
    email = data.get("email", None).lower()
    password = data.get("password", None)
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        response_body['error'] = 'El correo electrónico ya está registrado'
        return jsonify(response_body), 400
    user = Users()
    user.email = email
    user.password = password
    user.is_active = True
    user.first_name = data.get('first_name', None)
    user.last_name = data.get('last_name', None)
    user.age = data.get('age', None)
    user.is_admin = False
    db.session.add(user)
    db.session.commit()
    cart = Carts()
    cart.user_id = user.id
    cart.status = "inactivo"
    db.session.add(cart)
    db.session.commit()
    access_token = create_access_token(identity={'user_id': user.id})
    response_body['message'] = 'Usuario registrado y logueado'
    response_body['access_token'] = access_token
    return jsonify(response_body), 200

@api.route("/login", methods=["POST"])
def login():
    response_body = {}
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = db.session.execute(db.select(Users).where(Users.email == email, Users.password == password, Users.is_active == True)).scalar()
    if user:
        access_token = create_access_token(identity={'user_id': user.id, 'is_admin': user.is_admin})
        response_body['message'] = 'User logged in'
        response_body['access_token'] = access_token
        response_body['results'] = user.serialize()
        cart = Carts.query.filter_by(user_id=user.id).first()
        if cart:
            cart_items = db.session.execute(db.select(CartItems).where(CartItems.cart_id == cart.id)).scalars()
            items_serialized = [item.serialize() for item in cart_items]
            items_carts = []
            for row in items_serialized:
                product = db.session.execute(db.select(Products).where(Products.id == row['product_id'])).scalar()
                if product:
                    row['product_name'] = product.name
                    items_carts.append(row)
            response_body['cart'] = items_carts
        else:
            new_cart = Carts(user_id=user.id, status='en proceso')
            db.session.add(new_cart)
            db.session.commit()
            cart_items = db.session.execute(db.select(CartItems).where(CartItems.cart_id == new_cart.id)).scalars()
            items_serialized = [item.serialize() for item in cart_items]
            response_body['cart'] = items_serialized
        return response_body, 200
    else:
        response_body['message'] = 'Bad user or password'
        return response_body, 401
@api.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    response_body = {}
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    user = Users.query.get(current_user)
    response_body['message'] = f'User logeado: {current_user}'
    return response_body, user.serialize, 200


@api.route('/users', methods=['GET'])
def get_users():
    response_body = {}
    if request.method == 'GET':
        rows = db.session.execute(db.select(Users)).scalars()
        results = [row.serialize() for row in rows]
        response_body['results'] = results
        response_body['message'] = 'Listado de Usuarios'
        return response_body, 200

@api.route('/pedidos', methods=['GET'])
def get_pedidos():
    response_body = {}
    user_id = request.jwt_payload['user_id']
    rows = db.session.execute(
        db.select(OrderItems).join(Orders).where(Orders.user_id == user_id)
    ).scalars()
    results = [row.serialize() for row in rows]
    response_body['results'] = results
    response_body['message'] = 'Listado de Pedidos del Usuario'
    return response_body, 200

