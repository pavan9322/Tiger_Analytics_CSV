from flask import Flask, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from app import Retail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'
db = SQLAlchemy(app)
app.secret_key = "Dev Testing"


@app.route('/id/<int:id>/', methods=['GET'])
def get_user_by_id(id):
    prod = Retail.query.get(id)
    data = {"ID": prod.id,
            "SKU": prod.sku,
            "Name": prod.product_name,
            "Email": prod.price}
    return jsonify(data), 200


@app.route('/name/<string:name>/', methods=['GET'])
def get_user_by_name(name):
    prod = Retail.query.filter_by(product_name=name).first()
    data = {"ID": prod.id,
            "SKU": prod.sku,
            "Name": prod.product_name,
            "Email": prod.price}
    return jsonify(data), 200


@app.route('/all/', methods=['GET'])
def get_all_user():
    products = Retail.query.all()
    return jsonify(Retail.serialize_list(products))


@app.route('/name/<string:name>/', methods=['GET'])
def get_user_by_price(name):
    prod = Retail.query.filter_by(price=name).first()
    data = {"ID": prod.id,
            "SKU": prod.sku,
            "Name": prod.product_name,
            "Email": prod.price}
    return jsonify(data), 200


if __name__ == '__main__':
    db.create_all()
    app.run()