from flask import current_app as app
from backend.models import *
from flask_security import SQLAlchemyUserDatastore, hash_password

with app.app_context():
    db.create_all()

    userdatastore: SQLAlchemyUserDatastore = app.security.datastore

    # Create roles if they do not exist
    admin_role = userdatastore.find_or_create_role(name='admin', description='super user')
    customer_role = userdatastore.find_or_create_role(name='customer', description='general customer user')
    professional_role = userdatastore.find_or_create_role(name='professional', description='general professional user')

    # Create admin user
    if not userdatastore.find_user(email='admin.household@gmail.com'):
        userdatastore.create_user(
            email='admin.household@gmail.com',
            password=hash_password('pass'),
            roles=[admin_role]
        )

    db.session.commit()
