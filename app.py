from flask import Flask,jsonify,request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields,validate, ValidationError 
from sqlalchemy.orm import relationship
from sqlalchemy import text

# (myvenvalch)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:password@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

#------------------------------------------------------------------------------------------------------
#                                   SQL Table Classes
class Customer(db.Model):
  __tablename__ = "Customers"
  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(255),nullable=False) 
  email = db.Column(db.String(320))
  phone = db.Column(db.String(15))
  orders = db.relationship("Order", backref="customer")

# many to many relationship
order_product = db.Table("Order_Product",
  db.Column("order_id",db.Integer,db.ForeignKey('Orders.id'),primary_key=True),
  db.Column("product_id",db.Integer,db.ForeignKey("Products.id"),primary_key=True)
  )


class Order(db.Model):
  __tablename__ = "Orders"
  id = db.Column(db.Integer,primary_key=True)
  order_date = db.Column(db.DATETIME,server_default=text('CURRENT_TIMESTAMP'))
  delivery_date = db.Column(db.DATETIME)
  customer_id = db.Column(db.Integer,db.ForeignKey("Customers.id"))
  products = relationship("Product", secondary=order_product, back_populates="orders")

class Product(db.Model):
  __tablename__ = "Products"
  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(255),nullable=False) 
  price = db.Column(db.Float, nullable=False)
  quantity = db.Column(db.Integer,nullable=False)
  orders = relationship("Order", secondary=order_product, back_populates="products")

# one to one relationship
class CustomerAccount(db.Model):
  __tablename__ = "Customer_Accounts"
  id = db.Column(db.Integer,primary_key=True)
  username = db.Column(db.String(255),unique=True, nullable=False)
  password = db.Column(db.String(255),nullable=False)
  customer_id = db.Column(db.Integer,db.ForeignKey("Customers.id"))
  customer = db.relationship("Customer", backref="Customer_account", uselist=False)

#------------------------------------------------------------------------------------------------------
#                                        Schema Tables

class CustomerSchema(ma.Schema):
  name = fields.String(required=True)
  email=fields.String(required=True)
  phone=fields.String(required=True)
  order = fields.Integer(required=False)
  class Meta:
    fields = ("name","email","phone","order","id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class OrderSchema(ma.Schema):
  order_date = fields.DateTime(required=False)
  delivery_date = fields.DateTime(required=False)
  customer_id=fields.Integer(required=True)
  products = fields.List(fields.Integer(),required=True)
  class Meta:
    fields = ('order_date','delivery_date',"customer_id","products","id")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

class ProductSchema(ma.Schema):
  name = fields.String(required=True, validate=validate.Length(min=1))
  price=fields.Float(required=True, validate=validate.Range(min=0))
  quantity=fields.Integer(required=True,validate=validate.Range())
  class Meta:
    fields = ("name","price","quantity","id")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class CartSchema(ma.Schema):
  customer_id = fields.Integer(required=True)
  delivery_date = fields.Date(required=True)
  product_id = fields.Integer(required=True)
  products = fields.List(fields.String(),required=True)
    
  class Meta:
    fields = ("customer_id","order_date",'delivery_date' ,"products","id")

cart_schema = CartSchema()
carts_schema = CartSchema(many=True)

class CustomerAccountSchema(ma.Schema):
  username = fields.String(required=True)
  password=fields.String(required=True)
  customer_id=fields.Integer(required=True)
  class Meta:
    fields = ("username","password","customer_id","id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

# Initializing Database
with app.app_context():
  db.create_all()

#----------------------------------------------------------------------------
#                               Home Page
@app.route('/')
def home():
    return 'Welcome to our e-commerce app!'

#---------------------------------------------------------------------------------------------
#                                   Customer Functions For end routes
# getting all the customers in the database
@app.route("/customers",methods=["GET"])
def get_customer():
  customers = Customer.query.all()
  return customers_schema.jsonify(customers)

# adding a customer to the database
@app.route("/customers",methods=["POST"])
def create_customer():
  try:
    customer_data = customer_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  new_customer = Customer(name=customer_data["name"], email=customer_data["email"], phone=customer_data["phone"])
  db.session.add(new_customer)
  db.session.commit()
  return jsonify({"message": "New Customer Added Successfully!"}), 201


# PUT MEANS UPDATE
@app.route("/customers/<int:id>",methods=["PUT"])
def update_customer(id):
  customer = Customer.query.get_or_404(id)
  try:
    # Validates and deserialize the input
    customer_data = customer_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  
  customer.name = customer_data['name']
  customer.email = customer_data['email']
  customer.phone = customer_data['phone']
  db.session.commit()
  return jsonify({"message": "Customer details updated successfully"}), 200

# deleting the customer of your choice the <int:id> is to target the id of the customer to delete
@app.route("/customers/<int:id>",methods=["DELETE"])
def delete_customer(id):
  customer = Customer.query.get_or_404(id)
  db.session.delete(customer)
  db.session.commit()
  return jsonify({"message": "Customer removed successfully"}), 200

#-------------------------------------------------------------------------------------------------------
#                                          Order/Cart Functions For end routes
@app.route("/orders/status/<id>",methods=["GET"])
def order_status(id):
  order= Order.query.get_or_404(id)
  order_data = {
    'order_id': order.id,
    'order_date':order.order_date,
    'delivery_date':order.delivery_date,
    'customer':{
      'customer_id':order.customer.id,
      'name':order.customer.name,
      'email':order.customer.email,
      'phone':order.customer.phone
      }}
  return jsonify(order_data)


@app.route("/orders",methods=['GET'])
def get_orders():
  orders = Order.query.all()
  return carts_schema.jsonify(orders)


@app.route("/orders/<id>",methods=["GET"])
def get_order(id):
  order= Order.query.get_or_404(id)
  order_data = {
    'order_id': order.id,
    'order_date':order.order_date,
    'delivery_date':order.delivery_date,
    'customer':{
      'customer_id':order.customer.id,
      'name':order.customer.name,
      'email':order.customer.email,
      'phone':order.customer.phone
      },
    'products':[]
  }
  for product in order.products:
    product_data = {
      'product_id':product.id,
      'name':product.name,
      'price':product.price
    }
    order_data['products'].append(product_data)    
  return jsonify(order_data)


@app.route("/orders",methods=["POST"])
def create_order():
  try:
    order_data = order_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  new_order = Order(customer_id = order_data["customer_id"])
  for product_id in order_data["products"]:
    product = Product.query.get_or_404(product_id)
    new_order.products.append(product)
  db.session.add(new_order)
  db.session.commit()
  return jsonify({"message": "New Order Added Successfully!"}), 201


@app.route("/orders/<int:id>",methods=["DELETE"])
def delete_order(id):
  order = Order.query.get_or_404(id)
  db.session.delete(order)
  db.session.commit()
  return jsonify({"message": "Order removed successfully"}), 200

#----------------------------------------------------------------------------
#                              Product Functions For end routes   

@app.route("/products",methods=["GET"])
def get_product():
  products = Product.query.all()
  return products_schema.jsonify(products)


@app.route("/product/<int:id>",methods=["PUT"])
def update_product(id):
  product = Product.query.get_or_404(id)
  try:
    # Validates and deserialize the input
    product_data = product_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  product.name = product_data['name']
  product.price = product_data['price']
  product.quantity = product_data['quantity']
  db.session.commit()
  return jsonify({"message": "Product details updated successfully"}), 200


@app.route("/products",methods=["POST"])
def create_product():
  try:
    product_data = product_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  new_product = Product(name=product_data['name'],price=product_data['price'],quantity=product_data['quantity'])
  db.session.add(new_product)
  db.session.commit()
  return jsonify({"message": "Product has been added successfully"}), 201


@app.route("/products/<int:id>",methods=["DELETE"])
def delete_product(id):
  product = Product.query.get_or_404(id)
  db.session.delete(product)
  db.session.commit()
  return jsonify({"message": "Product removed successfully"}), 200


#------------------------------------------------------------------------
#                                 Customer Accounts Functions For end routes


@app.route("/customer_account",methods=["GET"])
def get_customer_account():
  customer_accounts = CustomerAccount.query.all()
  return customer_accounts_schema.jsonify(customer_accounts)


@app.route("/customer_account/<int:id>",methods=["PUT"])
def update_customer_account(id):
  customer_account = CustomerAccount.query.get_or_404(id)
  try:
    # Validates and deserialize the input
    customer_account_data = customer_account_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  
  customer_account.username = customer_account_data['username']
  customer_account.password = customer_account_data['password']
  customer_account.customer_id = customer_account_data['customer_id']
  db.session.commit()
  return jsonify({"message": "Customer Account details has been updated successfully"}), 200


@app.route("/customer_account",methods=["POST"])
def create_customer_account():
  try:
    customer_account_data = customer_account_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  
  new_customer_account = CustomerAccount(username=customer_account_data['username'],password=customer_account_data['password'],customer_id=customer_account_data['customer_id'])
  db.session.add(new_customer_account)
  db.session.commit()
  return jsonify({"message": "New Customer Account has created successfully"}),201


@app.route("/customer/<int:id>",methods=["DELETE"])
def delete_customer_account(id):
  customer_account = CustomerAccount.query.get_or_404(id)
  db.session.delete(customer_account)
  db.session.commit()
  return jsonify({"message": "Customer Account has been removed successfully"}), 200

#------------------------------------------------------------------------
#                         advanced lookups


@app.route("/customers/by-email",methods=["GET"])
def get_customer_by_email():
  email = request.args.get("email")
  customer = Customer.query.filter_by(email=email).first()
  if customer:
    return customer_schema.jsonify(customer)
  else:
    return jsonify({"message": "Customer Not Found"}),404


@app.route("/products/by-name",methods=["GET"])
def get_product_by_name():
  name = request.args.get("name")
  # with filter i have to say the class for the Class.name==name
  product = Product.query.filter_by(name=name).first()
  if product:
    return product_schema.jsonify(product)
  else:
    return jsonify({"message": "Product Not Found"}),404


if __name__ == "__main__":
  app.run(debug=True)
