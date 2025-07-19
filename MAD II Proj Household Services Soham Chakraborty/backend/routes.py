from flask import current_app as app, jsonify, request , render_template, send_file
from sqlalchemy.sql import func
from flask_security import auth_required, verify_password, hash_password, current_user, login_required
from backend.models import *
from backend.config import *
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
import base64

from backend.celery.tasks import add, create_csv
from celery.result import AsyncResult

cache = app.cache
# Define the path where the uploaded files will be saved
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"Uploads folder created at: {UPLOAD_FOLDER}")



import os


datastore = app.security.datastore


@app.route('/')
def home():
    return render_template('index.html')

@app.get('/celery')
def celery():
    task = add.delay(10, 20)
    return {'task_id' : task.id}

@app.get('/get-celery-data/<id>')
def getData(id):
    result = AsyncResult(id)

    if result.ready():
        return {'result' : result.result}, 200
    else:
        return {'message' : 'task not ready'}, 405
    


@auth_required('token') 
@app.get('/get-csv/<id>')
def getCSV(id):
    result = AsyncResult(id)

    if result.ready():
        return send_file(f"./backend/celery/user-downloads/{result.result}"), 200
    else:
        return {'message' : 'task not ready'}, 405

@auth_required('token') 
@app.get('/create-csv')
def createCSV():
    task = create_csv.delay()
    return {'task_id' : task.id}, 200







    




@app.route('/protected')
@auth_required('token')
def protected():
    return '<h1>Accesible by auth user only</h1>'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Invalid inputs"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Invalid email"}), 404

    if not verify_password(password, user.password):
        return jsonify({"message": "Incorrect password"}), 400

    # Check verification status
    if any(role.name == 'professional' for role in user.roles):
        if not user.verified:
            return jsonify({"message": "Wait for Admin Verification"}), 403

    if user.roles[0].name in ['customer', 'professional'] and not user.active:
        return jsonify({"message": "Your account is blocked"}), 403

    return jsonify({
        'token': user.get_auth_token(),
        'email': user.email,
        'role': user.roles[0].name,
        'id': user.id,
        'verified': user.verified,
        'blocked': not user.active
    }), 200





def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    role_name = request.form.get('role')  

    if not email or not password or role_name not in ['customer', 'professional']:
        return jsonify({"message": "Invalid inputs"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    try:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({"message": "Role not found"}), 400

        is_verified = True if role_name == 'customer' else False

        #new_user = datastore.create_user(email = email, password = hash_password(password), roles = [role], active = True)
        new_user = datastore.create_user(
            email=email,
            password=hash_password(password),
            roles=[role],
            active=True,
            verified=is_verified
        )
        db.session.add(new_user)
        db.session.commit()

        if role_name == 'customer':
            profile_pic = request.files.get('profile_pic')
            profile_pic_data = profile_pic.read() if profile_pic else None

            new_customer = Customer(
                user=new_user,
                name=request.form.get('name'),
                address=request.form.get('address'),
                pincode=request.form.get('pincode'),
                profile_pic=profile_pic_data
            )
            db.session.add(new_customer)

        elif role_name == 'professional':
            profile_pic = request.files.get('profile_pic')
            profile_pic_data = profile_pic.read() if profile_pic else None
            resume = request.files.get('resume')
            resume_data = resume.read() if resume else None

            new_professional = Professional(
                user=new_user,
                name=request.form.get('name'),
                address=request.form.get('address'),
                pincode=request.form.get('pincode'),
                description=request.form.get('description'),
                service_type=request.form.get('service_type'),
                experience=request.form.get('experience'),
                profile_pic=profile_pic_data,
                resume=resume_data,
                rating=0,
            )
            db.session.add(new_professional)

        db.session.commit()
        return jsonify({"message": "User created successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500




@app.route("/blockuser/<int:user_id>", methods=["POST"])
def block_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404
    user.active = False
    db.session.commit()
    return {"message": f"User {user.user_name} has been blocked"}, 200


@app.route("/unblockuser/<int:user_id>", methods=["POST"])
def unblock_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404
    user.active = True
    db.session.commit()
    return {"message": f"User {user.user_name} has been unblocked"}, 200




@app.route("/verifyprofessional/<int:user_id>", methods=["POST"])
def verify_professional(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not any(role.name == 'professional' for role in user.roles):
        return jsonify({"message": "User is not a professional"}), 400

    user.verified = True
    db.session.commit()

    return jsonify({"message": "Professional has been verified"}), 200









def get_verified_status(user):
    if user.roles[0].name == 'customer':  # Check if the role is 'customer'
        return True  # Customers are always verified
    elif user.roles[0].name == 'professional':  # Check if the role is 'professional'
        # Fetch verified status from the corresponding professional table
        professional = user.professional[0] if user.professional else None  # Access the first professional object
        return professional.verified if professional else False  # Return professional's verified status, or False if no professional info exists
    return False








@app.route("/admindashboard/usersview", methods=["GET"])
@auth_required('token')
@cache.cached(timeout = 5)
def view_users_to_admin():
    users = User.query.all()
    if not users:
        return {"message": "No users found"}, 404
    return jsonify([
        {
            'id': u.id,
            'name': (u.customer[0].name if u.customer else u.professional[0].name if u.professional else None),
            'address': (u.customer[0].address if u.customer else u.professional[0].address if u.professional else None),
            'pincode': (u.customer[0].pincode if u.customer else u.professional[0].pincode if u.professional else None),
            'email': u.email,
            'role': u.roles[0].name,  # Assuming users have one role, taking the first one
            'active': u.active,
            'verified': u.verified # Call the function to fetch verified status
        } 
        for u in users
    ])









@app.route('/admindashboard/statistics', methods=['GET'])
def get_admin_statistics():
    try:
        # Query total number of active customers
        total_customers = db.session.query(func.count(Customer.customer_id)).filter(
            User.id == Customer.user_id,
            User.active == True
        ).scalar()

        # Query total number of active professionals
        total_professionals = db.session.query(func.count(Professional.professional_id)).filter(
            User.id == Professional.user_id,
            User.active == True
        ).scalar()

        # Query number of blocked customers
        blocked_customers = db.session.query(func.count(Customer.customer_id)).filter(
            User.id == Customer.user_id,
            User.active == False
        ).scalar()

        # Query number of blocked professionals
        blocked_professionals = db.session.query(func.count(Professional.professional_id)).filter(
            User.id == Professional.user_id,
            User.active == False
        ).scalar()

        # Query number of ongoing service requests
        ongoing_requests = db.session.query(func.count(ServiceRequest.service_req_id)).filter(
            ServiceRequest.status.in_(['Pending', 'Accepted'])
        ).scalar()

        # Query number of completed service requests
        closed_requests = db.session.query(func.count(ServiceRequest.service_req_id)).filter(
            ServiceRequest.status == 'Completed'
        ).scalar()

        # Query distribution of professionals across services
        professional_distribution_rows = db.session.query(
            Professional.service_type, func.count(Professional.professional_id)
        ).filter(User.id == Professional.user_id, User.active == True).group_by(
            Professional.service_type
        ).all()

        # Format the distribution into a dictionary
        professional_distribution = {row[0]: row[1] for row in professional_distribution_rows}

        # Build the response object
        response = {
            "totalCustomers": total_customers,
            "totalProfessionals": total_professionals,
            "blockedCustomers": blocked_customers,
            "blockedProfessionals": blocked_professionals,
            "serviceRequests": {
                "ongoing": ongoing_requests,
                "closed": closed_requests
            },
            "professionalDistribution": professional_distribution
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({"error": "Failed to fetch statistics"}), 500
    










@app.route('/resume/<int:user_id>', methods=['GET'])
def get_resume(user_id):
    professional = Professional.query.filter_by(user_id=user_id).first()
    if professional and professional.resume:
        return send_file(
            BytesIO(professional.resume),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{professional.name}_resume.pdf"
        )
    return {"message": "Resume not available"}, 404








@app.route('/profilepic/<int:user_id>', methods=['GET'])
def get_profile_pic(user_id):
    profile = (
        Customer.query.filter_by(user_id=user_id).first() or 
        Professional.query.filter_by(user_id=user_id).first()
    )
    if profile and profile.profile_pic:
        encoded_pic = base64.b64encode(profile.profile_pic).decode('utf-8')
        return jsonify({"profile_pic_base64": encoded_pic}), 200
    return {"message": "Profile picture not set"}, 404








@app.route("/customerdashboard/<int:customer_id>", methods=["GET"])
#@login_required
@auth_required('token')
@cache.cached(timeout = 5)
def view_customer_dashboard(customer_id):
    customer = User.query.filter_by(id=customer_id).first()
    if not customer:
        return {"message": "Customer not found"}, 404

    query = db.session.query(Professional).join(User, User.id == Professional.user_id).filter(User.verified == True, User.active == True)

    # Get search parameters from request args
    name = request.args.get('name')
    address = request.args.get('address')
    pincode = request.args.get('pincode')
    service_type = request.args.get('service_type')

    if name:
        query = query.filter(Professional.name.ilike(f"%{name}%"))
    if address:
        query = query.filter(Professional.address.ilike(f"%{address}%"))
    if pincode:
        query = query.filter(Professional.pincode == int(pincode))
    if service_type:
        query = query.filter(Professional.service_type.ilike(f"%{service_type}%"))

    professionals = query.all()

    if not professionals:
        return {"message": "No professionals found"}, 404

    professional_list = [
        {
            "id": p.user_id,
            "name": p.name,
            "address": p.address,
            "pincode": p.pincode,
            "email": p.user.email,
            "description": p.description,
            "service_type": p.service_type,
            "experience": p.experience,
            "profile_pic": base64.b64encode(p.profile_pic).decode("utf-8") if p.profile_pic else None,
        }
        for p in professionals
    ]
    return jsonify(professional_list), 200









@app.route("/customerinfo/<int:customer_id>", methods=["GET"])
@auth_required('token')
@cache.cached(timeout=5)
def get_customer_info(customer_id):
    customer = Customer.query.filter_by(user_id=customer_id).first()

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    customer_data = {
        "name": customer.name,
        "address": customer.address,
        "pincode": customer.pincode
    }
    
    return jsonify(customer_data), 200











@app.route("/professionaldashboard/<int:professional_id>", methods=["GET", "POST"])
#@login_required
@auth_required('token')
@cache.cached(timeout = 5)
def view_professional_dashboard(professional_id):
    professional = User.query.filter_by(id=professional_id).first()
    if not professional:
        return {"message": "Professional not found"}, 404

    # Get all customers for this professional
    customers = User.query.filter(User.roles.any(Role.name == 'customer')).all()

    if not customers:
        return jsonify([]), 200

    # Prepare customer data
    customer_data = []
    for customer in customers:
        service_requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
        customer_data.append({
            'id': customer.id,
            'name': customer.name,
            'address': customer.address,
            'pincode': customer.pincode,
            'email': customer.email,
            'serviceRequests': [{'id': req.service_req_id, 'status': req.status} for req in service_requests]
        })

    return jsonify(customer_data), 200











@app.route('/professionaldashboard/<int:professional_id>/allservicerequests', methods=['GET'])
@login_required
@cache.cached(timeout = 5)
def get_all_service_requests(professional_id):
    # Validate the professional
    professional = User.query.filter_by(id=professional_id).first()
    if not professional:
        return jsonify({"message": "Professional not found"}), 404

    # Fetch all service requests associated with this professional
    service_requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()

    if not service_requests:
        return jsonify([]), 200

    # Group service requests by their status
    result = {
        "Pending": [],
        "Accepted": [],
        "Completed": [],
        "Rejected": [],
        "Cancelled": []
    }

    for req in service_requests:
        request_data = {
            "id": req.service_req_id,
            "customer_name": User.query.get(req.customer_id).customer[0].name,
            "status": req.status,
            "address": req.address,
            "pincode": req.pincode,
            "request_date": req.request_date.strftime('%Y-%m-%d'),
        }
        result[req.status].append(request_data)

    return jsonify(result), 200

















@app.route("/professionalinfo/<int:professional_id>", methods=["GET"])
def get_professional_details(professional_id):
    professional = Professional.query.filter_by(user_id=professional_id).first()
    
    if not professional:
        return jsonify({"message": "Professional not found"}), 404

    professional_data = {
        'name': professional.name,
        'address': professional.address,
        'pincode': professional.pincode,
        'service_type': professional.service_type,
        'experience': professional.experience,
        'rating': float(professional.rating),
    }

    return jsonify(professional_data), 200












@app.route('/createservice', methods=['POST'])
def create_service():
    data = request.get_json()
    name = data.get('name')
    base_price = data.get('base_price')
    time_required = data.get('time_required')
    description = data.get('description')

    service = Services(name=name, base_price=base_price, time_required=time_required, description=description)
    db.session.add(service)
    db.session.commit()

    return jsonify({"message": "service created"}), 200












@app.route("/admindashboard/servicesview", methods=["GET", "POST"])
def view_services_to_admin():
    services = Services.query.all()
    if not services:
        return {"message": "No services found"}, 404
    return jsonify([{'id': s.service_id, 'name': s.name, 'base_price': s.base_price, 'time_required': s.time_required, 'description': s.description} for s in services])











@app.route('/services', methods=['GET'])
def get_services():
    services = Services.query.all()
    if not services:
        return {"message": "No services found"}, 404
    return jsonify([{'name': s.name, 'base_price': s.base_price, 'time_required': s.time_required, 'description': s.description} for s in services])








@app.route("/admindashboard/service/<int:service_id>", methods=["PATCH"])
def update_service(service_id):
    data = request.get_json()

    # Fetch the service by its ID
    service = Services.query.filter_by(service_id=service_id).first()

    if not service:
        return {"message": "Service not found"}, 404

    try:

        service.name = data.get('name', service.name)
        service.base_price = data.get('base_price', service.base_price)
        service.time_required = data.get('time_required', service.time_required)
        service.description = data.get('description', service.description)

        db.session.commit()

        return {"message": "Service updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"An error occurred: {str(e)}"}, 500










@app.route("/admindashboard/service/<int:service_id>", methods=["DELETE"])
def delete_service(service_id):
    # Fetch the service by its ID
    service = Services.query.filter_by(service_id=service_id).first()

    if not service:
        return {"message": "Service not found"}, 404

    try:
        # Delete the service from the database
        db.session.delete(service)
        db.session.commit()

        return {"message": "Service deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"An error occurred: {str(e)}"}, 500








@app.route('/servicerequest', methods=['POST'])
def create_service_request():
    data = request.get_json()


    customer_id = data.get('customerId')
    professional_id = data.get('professionalId')
    address = data.get('address')
    pincode = data.get('pincode')

    # Validate required fields
    if not all([customer_id, professional_id, address, pincode]):
        return jsonify({"error": "Missing required fields. Please provide all details."}), 400

    try:
        # Create a new service request
        service_request = ServiceRequest(
            customer_id=customer_id,
            professional_id=professional_id,
            request_date=datetime.now(),
            status='Pending',
            address=address,
            pincode=pincode,
        )

        db.session.add(service_request)
        db.session.commit()

        return jsonify({"message": "Service request created successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error creating service request: {str(e)}"}), 500







@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    customer = Customer.query.filter_by(user_id=customer_id).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({
        "address": customer.address,
        "pincode": customer.pincode
    }), 200







@app.route("/customerdashboard/servicerequests/<int:customer_id>", methods=["GET"])
def get_customer_service_requests(customer_id):
    try:
        requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()
        
        if not requests:
           return jsonify({"message": "No service requests found."}), 

        service_requests = []
        for req in requests:
            professional = User.query.get(req.professional_id)
            professional_name = professional.professional[0].name
            service_requests.append({
                'id': req.service_req_id,
                'professional_name': professional_name,
                'status': req.status,
                'reviewed': req.reviewed,
                'action': 'Cancel' if req.status == 'Pending' else 'Review' if req.status == 'Completed' else None
            })
        
        return jsonify(service_requests), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving service requests: {str(e)}"}), 500









@app.route("/professionaldashboard/servicerequests/<int:customer_id>", methods=["GET"])
@cache.cached(timeout = 5)
def get_professional_service_requests(customer_id):
    # Fetch all service requests related to the provided customer ID
    requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()
    
    # If no requests exist, return an empty list
    if not requests:
        return jsonify([]), 200

    service_requests = []
    for req in requests:
        professional = User.query.get(req.professional_id)  # Fetch professional info
        if professional:
            service_requests.append({
                'id': req.service_req_id,
                'professional_name': professional.user_name,  # Name of the assigned professional
                'status': req.status,
                'action': 'Accept' if req.status == 'Pending' else 'Mark Complete' if req.status == 'Accepted' else None,
            })

    return jsonify(service_requests), 200










@app.route("/professionaldashboard/<int:professional_id>/servicerequests/<int:customer_id>", methods=["GET"])
@login_required
def get_service_requests_for_customer(professional_id, customer_id):
    # Get service requests for the specific customer handled by the professional
    service_requests = ServiceRequest.query.filter_by(customer_id=customer_id, professional_id=professional_id).all()

    if not service_requests:
        return jsonify([]), 200

    result = []
    for req in service_requests:
        result.append({
            'id': req.service_req_id,
            'customer_name': User.query.get(req.customer_id).user_name,
            'status': req.status,
            'action': 'Accept' if req.status == 'Pending' else 'Mark Complete' if req.status == 'Accepted' else None,
        })

    return jsonify(result), 200








@app.route("/professionaldashboard/<int:professional_id>/servicerequests/<int:service_request_id>", methods=["PATCH"])
@login_required
def update_service_request_status(professional_id, service_request_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Accepted", "Completed", "Rejected"]:
        return {"message": "Invalid status"}, 400

    service_request = ServiceRequest.query.get(service_request_id)
    if not service_request:
        return {"message": "Service request not found"}, 404

    # Ensure that the service request is linked to the professional
    if service_request.professional_id != professional_id:
        return {"message": "You are not authorized to update this service request"}, 403

    service_request.status = new_status
    db.session.commit()

    return {"message": "Service request updated successfully"}, 200











@app.route("/servicerequest/action/<int:request_id>", methods=["POST"])
def handle_service_request_action(request_id):
    data = request.json
    action = data.get("action")

    request = ServiceRequest.query.get(request_id)
    if not request:
        return {"message": "Service request not found."}, 404

    if action == "Accept":
        request.status = "Accepted"
    elif action == "Mark Complete":
        request.status = "Completed"
    else:
        return {"message": "Invalid action."}, 400

    db.session.commit()
    return {"message": "Action completed successfully."}, 200









@app.route('/servicerequest/<int:service_req_id>/cancel', methods=['POST'])
def cancel_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    if not service_request:
        return {"message": "Service request not found."}, 404
    service_request.status = 'Cancelled'
    db.session.commit()
    return jsonify({"message": "Service request cancelled."}), 200













@app.route('/servicerequest/<int:service_request_id>/review', methods=['POST'])
def submit_review(service_request_id):
    data = request.json
    rating = data.get('rating')
    review_text = data.get('reviewText')

    # Validate the input
    if not (rating and review_text):
        return jsonify({'error': 'Rating and review text are required'}), 400

    # Fetch the service request
    service_request = ServiceRequest.query.get(service_request_id)
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404

    # Ensure the service request has not already been reviewed
    if service_request.reviewed:
        return jsonify({'error': 'Service request has already been reviewed'}), 400

    # Add the review
    review = Reviews(
        service_request_id=service_request_id,
        rating=rating,
        review_text=review_text,
        reviewed_at=datetime.utcnow()
    )
    db.session.add(review)

    # Mark the service request as reviewed
    service_request.reviewed = True

    # Update the professional's rating
    professional_id = service_request.professional_id
    professional = Professional.query.filter_by(user_id=professional_id).first()

    if professional:
        # Fetch all reviews where the service request is reviewed
        all_reviews = (
            Reviews.query
            .join(ServiceRequest, Reviews.service_request_id == ServiceRequest.service_req_id)
            .filter(ServiceRequest.professional_id == professional_id, ServiceRequest.reviewed == True)
            .all()
        )

        # Calculate the new average rating
        total_reviews = len(all_reviews)
        total_rating = sum([r.rating for r in all_reviews])
        professional.rating = round(total_rating / total_reviews, 1) if total_reviews > 0 else 0

    db.session.commit()

    return jsonify({'message': 'Review submitted successfully'}), 201
    











@app.route('/servicerequest/<int:service_request_id>/review', methods=['GET'])
def get_review(service_request_id):
    review = Reviews.query.filter_by(service_request_id=service_request_id).first()
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    return jsonify({
        'rating': str(review.rating),
        'reviewText': review.review_text,
    }), 200










@app.route("/customerdashboard/search", methods=["GET"])
@login_required
def search_professionals():
    # Get search parameters from the request query string
    name = request.args.get('name', '')
    address = request.args.get('address', '')
    pincode = request.args.get('pincode', '')
    service_type = request.args.get('service_type', '')
    
    # Query to search professionals
    query = db.session.query(Professional).join(User, User.id == Professional.user_id).filter(User.verified == True, User.active == True)
    
    if name:
        query = query.filter(Professional.name.ilike(f'%{name}%'))
    if address:
        query = query.filter(Professional.address.ilike(f'%{address}%'))
    if pincode:
        query = query.filter(Professional.pincode == pincode)
    if service_type:
        query = query.filter(Professional.service_type.ilike(f'%{service_type}%'))
    
    professionals = query.all()

    
    professional_list = [
        {
            "id": p.user_id,
            "name": p.name,
            "address": p.address,
            'pincode': p.pincode,
            "email": p.user.email,
            "description": p.description,
            "service_type": p.service_type,
            "experience": p.experience,
            "profile_pic": base64.b64encode(p.profile_pic).decode("utf-8") if p.profile_pic else None,
        }
        for p in professionals
    ]
    
    return jsonify(professional_list), 200











@app.route('/professional/profile/<int:professional_id>', methods=['GET'])
def get_professional_profile(professional_id):
    professional = Professional.query.filter_by(user_id=professional_id).first()
    if not professional:
        return jsonify({"error": "Professional not found"}), 404

    profile_data = {
        "id":professional.user_id,
        "name": professional.name,
        "description": professional.description,
        "service_type": professional.service_type,
        "experience": professional.experience,
        "profile_pic": base64.b64encode(professional.profile_pic).decode('utf-8') if professional.profile_pic else None,
    }
    return jsonify(profile_data)

