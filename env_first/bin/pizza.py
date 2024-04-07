from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza_restaurants.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Restaurant(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    
    pizzas = db.relationship('Pizza',
                             secondary='restaurant_pizza',
                             backref='restaurants')

class Pizza(db.Model):
    
    id = db.Column(db.Integer, 
                   primary_key=True)
    name = db.Column(db.String(50), 
                     nullable=False)
    ingredients = db.Column(db.String(100),
                            nullable=False)

class RestaurantPizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    price = db.Column(db.Float, nullable=False)
    pizza_id = db.Column(db.Integer,
                         db.ForeignKey('pizza.id'),
                         nullable=False)
    restaurant_id = db.Column(db.Integer,
                              db.ForeignKey('restaurant.id'),
                              nullable=False)

    def validate_price(self):
        return 1 <= self.price <= 30



@app.route('/restaurants', methods=['GET'])

def get_restaurants():
    
    restaurants = Restaurant.query.all()
    data = [{'id': restaurant.id, 
             'name': restaurant.name, 
             'address': restaurant.address} for restaurant in restaurants]
    return jsonify(data)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if restaurant:
        pizzas = [{'id': pizza.id,
                   'name': pizza.name,
                   'ingredients': pizza.ingredients}
                  for pizza in restaurant.pizzas]
        return jsonify({'id': restaurant.id, 'name':
            restaurant.name,
            'address': restaurant.address, 'pizzas': pizzas})
    else:
        
        return jsonify({'error': 'Restaurant not found'}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])

def delete_restaurant(id):
    
    restaurant = Restaurant.query.get(id)
    if restaurant:
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    
    else:
        return jsonify({'error': 'Restaurant not found'}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    
    pizzas = Pizza.query.all()
    data = [{'id': pizza.id,
             'name': pizza.name, 
             'ingredients': pizza.ingredients} for pizza in pizzas]
    return jsonify(data)




@app.route('/restaurant_pizzas', methods=['POST'])

def create_restaurant_pizza():
    
    data = request.json
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    
    if price is None or pizza_id is None or restaurant_id is None:
        
        return jsonify({'errors': ['Missing required fields']}), 400

    if not (1 <= price <= 30):
        
        return jsonify({'errors': ['Price must be between 1 and 30']}), 400

    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

    try:
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        pizza = Pizza.query.get(pizza_id)
        return jsonify({'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients}), 201
    
    except IntegrityError:
        
        db.session.rollback()
        return jsonify({'errors': ['Integrity error']}), 400

if __name__ == '__main__':
    
    db.create_all()
    app.run(debug=True)