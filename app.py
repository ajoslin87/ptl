from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import ftx_api_calls
import yfinance as yf
# import talib
from technical.cdlstick import Mqttcalls
import pandas as pd

#Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Init db
db = SQLAlchemy(app)
#Init ma
ma = Marshmallow(app)

#Product Class/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self,name,description,price,qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id','name','description','price','qty')

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create Product
@app.route('/product/<ticker>',methods=['Post'])
def get_data(ticker):
    result = Mqttcalls.get_data(ticker)
    return product_schema.jsonify(new_product)

# Get All Products
@app.route('/historical/<id>/<start>/<end>/', methods=['GET'])
def run_function(id, start, end):
    result = yf.download(id, start, end)
    return result.to_json()

# FTX Market Buy

@app.route('/ftx-market-buy/<id>/', methods=['GET'])
def send_ftx_buy(id):
    ftx_api_calls.market_buy(id)

#FTX Historical

@app.route('/ftx/<id1>/<id2>/', methods=['GET']) 
def get_ftx_historical(id1, id2):
    idCombined = id1 + "/" + id2
    result = ftx_api_calls.ftx_historical(idCombined)
    # morningstar = Mqttcalls.get_data(result)
    # result['morningstar'] = morningstar
    # print(result)
    # for candle in result:
    #     print(candle)
    #     return jsonify(candle)
    print(jsonify(result))
    return jsonify(result)
    # return morningstar

@app.route('/candle/<id1>/<id2>/', methods=['GET'])
def get_candle(id1, id2):
    idCombined = id1 + "/" + id2
    result = ftx_api_calls.ftx_historical(idCombined)
    df = pd.DataFrame(result, columns=['Date', 'Open', 'High', 'Low', 'Close','Volume'])
    morningstar = Mqttcalls.get_data(df)
    df['Morningstar'] = morningstar
    print(df)
    # print(type(morningstar))
    # print(type(result))
    return df.to_json()
    # return morningstar
    
# # Get Single Product
# @app.route('/product/<id>', methods=['GET'])  
# def get_product(id):
#     product = Product.query.get(id)
#     return product_schema.jsonify(product)

# Delete Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)

    db.session.commit()

    db.session.delete(product)

# Update Product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name
    product.description = description 
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)
# Run Server
if __name__ == '__main__': 
    app.run(debug=True)


 