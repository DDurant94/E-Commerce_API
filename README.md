# E-Commerce API

Author: Daniel Durant

GitHub:

https://github.com/DDurant94

Summary: 

This program is Flask web application for an E-Commerce platform. It defines several routes that handle HTTP requests related 
to customers and orders. 'E-Commerce API' can be scaled up to handle larger web applications, your imagination is the limit to this 
RESTful API. Bring Flask, Marsmallow, MySQL, and SQLAlchemy all into one cohesive masterpiece for E-Commerce operations for safe 
storage of vital information. 


Imports: 
1. from flask import Flask,jsonify,request
2. from flask_marshmallow import Marshmallow
3. from flask_sqlalchemy import SQLAlchemy
4. from marshmallow import fields,validate, ValidationError 
5. from sqlalchemy.orm import relationship
6. from sqlalchemy import text

PIP Installs:
1. blinker                1.8.2
2. click                  8.1.7
3. colorama               0.4.6
4. Flask                  3.0.3
5. flask-marshmallow      1.2.1
6. Flask-SQLAlchemy       3.1.1
7. greenlet               3.0.3
8. itsdangerous           2.2.0
9. Jinja2                 3.1.4
10. MarkupSafe             2.1.5
11. marshmallow            3.21.2
12. mysql-connector-python 8.4.0
13. packaging              24.0
14. pip                    24.0
15. SQLAlchemy             2.0.30
16. typing_extensions      4.11.0
17. Werkzeug               3.0.3


# Database Configuration: 
The API connects to a MySQL database named e_commerce_db using MySQL Connector.

ORM Models:

Customer: 

Represents customers with attributes like name, email, and phone. It has a one-to-many relationship with the Order model.

Order: 

Contains order details including order and delivery dates. It is linked to Customer and Product models through foreign keys 
and a many-to-many relationship.

Product: 

Stores product information such as name, price, and quantity. It is part of the many-to-many relationship with the Order model.

CustomerAccount: 

Manages customer account details with a one-to-one relationship with the Customer model.

Relationships:

A many-to-many relationship between Order and Product models, allowing multiple products to be associated with a single order 
and vice versa. A one-to-one relationship between Customer and CustomerAccount models, ensuring each customer has a unique account.
Security Note: Your database URI contains sensitive information (password). Make sure to keep it secure and consider using 
environment variables for such credentials. This API is structured to handle typical e-commerce operations, including managing 
customers, orders, products, and user accounts. It’s designed to be flexible and scalable, accommodating the complex relationships 
between different data entities.

Marshmallow Schemas: 

The CustomerSchema, OrderSchema, ProductSchema, CartSchema, and CustomerAccountSchema are defined using Marshmallow’s Schema class.

These schemas are responsible for:

Validation: 

Ensuring that the data meets certain criteria before it’s saved to the database 
(e.g., name must be a string, price must be a float greater than 0).

Serialization: 

Converting complex data types, like SQL rows, into JSON-friendly formats.

Deserialization: 

Loading JSON data into SQLAlchemy models.

Fields: 

Each schema defines various fields that correspond to the database model attributes. For example, CustomerSchema has 
name, email, phone, and order fields.

Meta Class: 

Inside each schema’s Meta class, the fields attribute lists the fields that should be included when the schema is used to 
serialize or deserialize data.

Schema Instances: 

Instances of these schemas are created to handle single objects (customer_schema, order_schema, etc.) and collections of objects 
(customers_schema, orders_schema, etc.).

Database Initialization: 

At the end of the code, within the Flask application context, db.create_all() is called to create all the tables in the database 
according to the defined models.  This setup is typical for Flask applications that require an API to communicate with a front-end 
by sending and receiving JSON data. The schemas act as a bridge between the SQLAlchemy models and the JSON format required by the 
front-end. The many=True parameter in the collection schemas allows for the processing of multiple objects at once, which is 
useful for batch operations. The code also implies that the application will handle e-commerce functionalities like managing 
customers, orders, products, and customer accounts. The use of Marshmallow makes it easier to validate and serialize the data, 
ensuring that the API endpoints send and receive data in the correct format.
