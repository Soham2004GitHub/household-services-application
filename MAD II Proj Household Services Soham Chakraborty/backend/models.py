from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_security import UserMixin, RoleMixin


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True, unique=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    verified = db.Column(db.Boolean, default = True)
    fs_uniquifier = db.Column(db.String, nullable=False)
    roles = db.relationship('Role', backref='user', secondary='userroles')
    customer = db.relationship('Customer', backref = 'user')
    professional = db.relationship('Professional', backref = 'user')




class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, unique = True, nullable  = False)
    description = db.Column(db.String, nullable = False)

class UserRoles(db.Model):
    __tablename__ = 'userroles'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    profile_pic = db.Column(db.LargeBinary)
    servicerequests = db.relationship('ServiceRequest', back_populates='customer')

class Professional(db.Model):
    __tablename__ = 'professional'
    professional_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    service_type = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    profile_pic = db.Column(db.LargeBinary)
    rating = db.Column(db.Numeric(2, 1), nullable=False, default=0)
    resume = db.Column(db.LargeBinary)
    servicerequests = db.relationship('ServiceRequest', back_populates='professional')

class ServiceRequest(db.Model):
    __tablename__ = 'servicerequest'
    service_req_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    request_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='Requested')
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    payment_status = db.Column(db.Boolean, nullable=False, default=False)
    reviewed = db.Column(db.Boolean, default = False)
    reviews = db.relationship('Reviews', backref='servicerequest')

    # Relationships
    customer = db.relationship('Customer', back_populates='servicerequests')
    professional = db.relationship('Professional', back_populates='servicerequests')

class Services(db.Model):
    __tablename__ = 'service'
    service_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    base_price = db.Column(db.Numeric(10,2), nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    updated_at = db.Column(db.DateTime)


class Reviews(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('servicerequest.service_req_id'), nullable=False)
    rating = db.Column(db.Numeric(3,2), nullable=False)
    review_text = db.Column(db.String(200))
    reviewed_at = db.Column(db.DateTime)
