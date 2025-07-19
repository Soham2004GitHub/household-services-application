from celery import shared_task
import time
from backend.models import *
import flask_excel
import csv
from backend.celery.mail_service import send_email
from sqlalchemy import and_, or_

@shared_task(ignore_result = False)
def add(x,y):
    time.sleep(10)
    return x+y

@shared_task(ignore_result = False)
def create_csv():
    results = db.session.query(
    ServiceRequest.service_req_id,
    ServiceRequest.customer_id,
    ServiceRequest.professional_id,
    ServiceRequest.status,
    ServiceRequest.address,
    Reviews.rating,
    Reviews.review_text,
    Reviews.reviewed_at
    ).join(Reviews, ServiceRequest.service_req_id == Reviews.service_request_id, isouter=True).filter(ServiceRequest.status == "Completed")
 

    filename = "service_requests_data.csv"
    column_names = [
    'service_req_id',
    'customer_id',
    'professional_id',
    'status',
    'address',
    'rating',
    'review_text',
    'reviewed_at']

    print(column_names)

    csv_out = flask_excel.make_response_from_query_sets(results, column_names = column_names, file_type='csv' )

    with open(f'./backend/celery/user-downloads/{filename}', 'wb') as file:
        file.write(csv_out.data)
    
    return filename

from celery import shared_task
from sqlalchemy import and_

@shared_task()
def daily_reminders():
    """
    Sends email reminders to professionals with pending service requests.
    """

    # Query all professionals with the role 'professional'
    professionals = User.query.filter(User.roles.any(Role.name == 'professional')).all()

    if not professionals:
        print("No professionals found.")
        return "No professionals found."

    print(f"Found {len(professionals)} professionals.")  # Debugging log

    # Dictionary to store email content for each professional
    email_content_map = {}

    # First loop: Construct email content for each professional
    for professional in professionals:
        if not professional.professional:
            print(f"User {professional.id} is marked as a Professional but has no Professional profile.")
            continue

        
        professional_id = professional.professional[0].user_id
        

        pending_requests = (
            ServiceRequest.query
            .filter(
                and_(
                    ServiceRequest.professional_id == professional_id,
                    ServiceRequest.status == 'Pending'
                )
            )
            .join(Customer, ServiceRequest.customer_id == Customer.user_id)  # Explicit join with Customer table
            .add_columns(
                ServiceRequest.address,
                ServiceRequest.pincode,
                Customer.name.label('customer_name')  # Alias for clarity
            )
            .all()
        )
        if not pending_requests:
            print(f"No pending requests found for {professional.email}.")
            continue

        print(f"Found {len(pending_requests)} pending requests for {professional.email}.")  # Debugging log

        # Construct the email content
        email_content = f"""
        <h2>Dear {professional.professional[0].name},</h2>
        <p>You have pending service requests that require your attention:</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Customer Name</th>
                <th>Address</th>
                <th>Pincode</th>
            </tr>
        """
        for request in pending_requests:
            
            email_content += f"""
            <tr>
                <td>{request.customer_name if request.customer_name else "N/A"}</td>
                <td>{request.address}</td>
                <td>{request.pincode}</td>
            </tr>
            """
        email_content += """
        </table>
        <p>Thank you.</p>
        <p>Regards,<br>Household Services</p>
        """

        # Add the email content to the dictionary
        email_content_map[professional.email] = email_content

    '''# Debugging: Check if the dictionary has any content
    if not email_content_map:
        print("No pending requests found for any professional.")
        return "No pending requests found."
    
    print(email_content_map)'''

    # Second loop: Send emails to each professional
    for email, content in email_content_map.items():
        try:
            send_email(email, "Pending Service Requests Alert", content)
            print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

    print("Processed all professionals.")
    return "Pending request alerts sent to all professionals."

import matplotlib.pyplot as plt
import io
import base64

from io import BytesIO
import matplotlib.pyplot as plt
import base64

@shared_task()
def monthly_reminders(): #Monthly report for all customers
    

    # Fetch all customers
    customers = Customer.query.all()

    if not customers:
        print("No customers found.")
        return "No customers found."

    print(f"Found {len(customers)} customers.")  # Debug log

   
    for customer in customers:
        
        pending_count = ServiceRequest.query.filter_by(customer_id=customer.user_id, status="Pending").count()
        cancelled_count = ServiceRequest.query.filter_by(customer_id=customer.user_id, status="Cancelled").count()
        accepted_count = ServiceRequest.query.filter_by(customer_id=customer.user_id, status="Accepted").count()
        rejected_count = ServiceRequest.query.filter_by(customer_id=customer.user_id, status="Rejected").count()
        completed_count = ServiceRequest.query.filter_by(customer_id=customer.user_id, status="Completed").count()
        reviews_given = ServiceRequest.query.filter_by(customer_id=customer.user_id, reviewed=True).count()

        # Prepare data for the pie chart
        labels = ['Pending', 'Cancelled', 'Accepted', 'Rejected', 'Completed']
        counts = [pending_count, cancelled_count, accepted_count, rejected_count, completed_count]
        colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2F0']

        # Exclude labels with 0 values for better presentation
        filtered_counts = [count for count in counts if count > 0]
        filtered_labels = [labels[i] for i in range(len(counts)) if counts[i] > 0]
        filtered_colors = [colors[i] for i in range(len(counts)) if counts[i] > 0]

        # Generate the pie chart
        fig, ax = plt.subplots()
        ax.pie(filtered_counts, labels=filtered_labels, colors=filtered_colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures the pie is circular.

        # Save the chart to a BytesIO object as a base64 image
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches="tight")
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)

        # Embed the chart in the email content
        email_content = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    text-align: left;
                    padding: 8px;
                }}
                th {{
                    background-color: #f4f4f4;
                }}
            </style>
        </head>
        <body>
            <h2>Dear {customer.name},</h2>
            <p>Here is your activity report:</p>
            <table>
                <tr>
                    <th>Activity</th>
                    <th>Count</th>
                </tr>
                <tr>
                    <td>Pending Services</td>
                    <td>{pending_count}</td>
                </tr>
                <tr>
                    <td>Cancelled Services</td>
                    <td>{cancelled_count}</td>
                </tr>
                <tr>
                    <td>Accepted Services</td>
                    <td>{accepted_count}</td>
                </tr>
                <tr>
                    <td>Rejected Services</td>
                    <td>{rejected_count}</td>
                </tr>
                <tr>
                    <td>Completed Services</td>
                    <td>{completed_count}</td>
                </tr>
                <tr>
                    <td>Reviews Given</td>
                    <td>{reviews_given}</td>
                </tr>
            </table>
            <p>Below is the distribution of your service requests:</p>
            <img src="data:image/png;base64,{chart_base64}" alt="Activity Distribution">
            <p>Thank you.</p>
            <p>Regards,<br>Household Services</p>
        </body>
        </html>
        """

        # Send the email to the customer
        try:
            send_email(customer.user.email, "Your Monthly Activity Report", email_content)
            print(f"Activity report sent to {customer.user.email}")
        except Exception as e:
            print(f"Failed to send activity report to {customer.user.email}: {e}")

    print("All customer activity reports have been processed.")
    return "Activity reports sent to all customers."


