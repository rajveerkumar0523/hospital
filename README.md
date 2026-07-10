<p align="center"> <img src="https://img.shields.io/badge/Django-5.x-success?style=for-the-badge&logo=django" /> <img src="https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql" /> <img src="https://img.shields.io/badge/Python-3.10-yellow?style=for-the-badge&logo=python" /> <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" /> </p>


🏥 Overview
MediCore is a full-stack Hospital Management System developed using Django and PostgreSQL.

The project digitizes the complete workflow of a hospital—from appointment booking to laboratory testing, payment collection, prescription generation, and medical record management.

Unlike basic CRUD hospital projects, MediCore follows a real hospital workflow with multiple user roles interacting together.


✨ Features
👨‍⚕️ Doctor
Secure Login
Dashboard
Manage Appointments
View Patient Details
Order Medical Tests
View Laboratory Reports
Write Prescription
Update Prescription
Complete Consultation
Cancel Appointment
View Previous Reports

🧪 Laboratory Technician
Dashboard
Paid Test Queue
Open Patient
Perform Laboratory Tests
Submit Test Results
View Completed Reports
Track Pending Tests
Report Status Management

🧾 Receptionist
Dashboard
Search Patients
View Pending Bills
Collect Cash Payment
Payment History
Today's Collection
Patients Served Counter

👤 Patient
Registration
Login
Dashboard
Book Appointment
View Appointment Status
View Lab Reports
View Prescriptions
Medical History

👨‍💼 Admin
Manage Users
Manage Departments
Manage Doctors
System Overview
Reports
Hospital Statistics

Complete Workflow
Patient
    │
    ▼
Book Appointment
    │
    ▼
Doctor Consultation
    │
    ├──────────────► No Test Required
    │                    │
    │                    ▼
    │              Write Prescription
    │                    │
    │                    ▼
    │             Consultation Complete
    │
    ▼
Order Medical Tests
    │
    ▼
Receptionist
Collect Test Payment
    │
    ▼
Payment Successful
    │
    ▼
Laboratory Dashboard
    │
    ▼
Perform Tests
    │
    ▼
Submit Laboratory Report
    │
    ▼
Doctor Reviews Report
    │
    ▼
Write Prescription
    │
    ▼
Appointment Completed
    │
    ▼
Patient Views Report & Prescription


Modules
accounts/
appointments/
dashboard/
doctor/
patient/
reception/
laboratory/
departments/
notifications/


📂 Project Structure
hospital/

│
├── apps/
│   ├── accounts/
│   ├── appointments/
│   ├── dashboard/
│   ├── doctor/
│   ├── patient/
│   ├── reception/
│   ├── laboratory/
│   └── departments/
│
├── static/
│
├── templates/
│
├── media/
│
├── hospital/
│
├── manage.py
│
└── requirements.txt


🛠️ Tech Stack
Backend
  Python
  Django
  Django ORM
  
Database
  PostgreSQL
  
Frontend
  HTML5
  CSS3
  JavaScript
  
Authentication
  Django Authentication
  Custom User Model
  Role Based Access Control
  
👥 User Roles
  Role	          Access
  Admin	          Full System
  Doctor	        Consultation, Prescription
  Laboratory      Technician	Tests & Reports
  Receptionist	  Payments
  Patient	        Appointment & Reports

  
📋 Appointment Status Flow
Pending

↓

Confirmed

↓

Awaiting Tests

↓

Report Ready

↓

Completed

Cancelled appointments are handled separately.



🧪 Laboratory Workflow
  Doctor Orders Test
  
      ↓
  
  Receptionist Collects Payment
  
      ↓
  
  Lab Technician Receives Test
  
      ↓
  
  Lab Performs Test
  
      ↓
  
  Result Submitted
  
      ↓
  
  Doctor Reviews Result
  
      ↓
  
  Prescription Generated

  
💳 Payment Workflow
  Pending Bill
  
      ↓
  
  Reception Dashboard
  
      ↓
  
  Collect Cash
  
      ↓
  
  Bill Paid
  
      ↓
  
  Lab Test Activated

  
📄 Prescription Workflow
  Doctor Consultation
  
      ↓
  
  Write Diagnosis
  
      ↓
  
  Add Medicines
  
      ↓
  
  Instructions
  
      ↓
  
  Follow-up Date
  
      ↓
      
  Prescription Saved
  
      ↓
  
  Patient Can View

  
📊 Dashboard Features
  Doctor Dashboard
  Appointment Filters
  Ready Reports
  Pending Tests
  View Report
  View Prescription
  Patient Details
  
Laboratory Dashboard
  Patients Waiting
  Pending Tests
  Completed Reports
  Test Queue
  Report Submission
  
Reception Dashboard
  Pending Bills
  Cash Collection
  Today's Revenue
  Recent Payments
  Patient Search
  
Patient Dashboard
  Upcoming Appointments
  Completed Consultations
  Prescriptions
  Laboratory Reports
  
🔒 Security
  CSRF Protection
  Login Required
  Role Based Permissions
  Protected Views
  Secure Authentication

  
📸 Screenshots
Login

Doctor Dashboard

Reception Dashboard

Laboratory Dashboard

Patient Dashboard

Appointment Detail

Lab Report

Prescription

Payment Screen

(Add screenshots here after uploading.)



⚙️ Installation
  Clone Repository
    git clone https://github.com/yourusername/MediCore.git
  
  Go to Project
    cd MediCore
    
  Create Virtual Environment
    Windows
      python -m venv venv
    macOS/Linux
      python3 -m venv venv

  Activate Environment
    Windows
      venv\Scripts\activate
    macOS/Linux
      source venv/bin/activate
      
  Install Dependencies
    pip install -r requirements.txt
    PostgreSQL Database

Create a PostgreSQL database.

Example:

CREATE DATABASE hospital_db;
Configure Environment Variables

Create a .env file:

SECRET_KEY=your_secret_key

DEBUG=True

DB_NAME=hospital_db

DB_USER=postgres

DB_PASSWORD=your_password

DB_HOST=localhost

DB_PORT=5432
Apply Migrations
python manage.py makemigrations

python manage.py migrate
Create Superuser
python manage.py createsuperuser
Run Server
python manage.py runserver

Open:

http://127.0.0.1:8000/


📦 Requirements
  Python 3.10+
  Django 5.x
  PostgreSQL
  psycopg2
  python-dotenv

  
🌟 Future Improvements
  Email Notifications
  SMS Notifications
  Online Payment Gateway
  PDF Prescription
  PDF Laboratory Report
  Medicine Inventory
  Pharmacy Module
  Bed Management
  Nurse Dashboard
  Billing Invoice PDF
  Doctor Availability Calendar
  Patient Timeline
  Analytics Dashboard
  REST API
  Mobile Application
  Docker Deployment

  
🤝 Contributing
  Contributions are welcome.
  Fork the repository.
  Create a feature branch.
  Commit your changes.
  Push the branch.
  Open a Pull Request.

  
📜 License
This project is licensed under the MIT License.
👨‍💻 Developer
   Rajveer Kumar
🎓 BCA Student
💻 Full Stack Django Developer
🇮🇳 India


⭐ Support
If you found this project useful:
⭐ Star the repository
🍴 Fork the repository
💡 Contribute to the project

❤️ Thank You

MediCore aims to simplify hospital operations through an integrated, role-based healthcare management system.
