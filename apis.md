1. Accounts
POST /api/accounts/login/

Payload:
{
  "username": "admin",
  "password": "admin"
}

Response:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "clinic@example.com",
    "role": "clinic",
    "is_staff": false
  }
}

POST /api/accounts/logout/
{
  "detail": "Successfully logged out."
}


2. Admin Panel / Clinic / Doctor / Patient / Appointment APIs

Dashboard: GET /api/admin-panel/dashboard/
Payload: None
Response:
{
  "total_clinics": 10,
  "total_doctors": 50,
  "total_patients": 200,
  "total_appointments": 150
}

## Clinics
GET /api/admin-panel/clinics/
[
  {
    "id": 1,
    "name": "Alpha Clinic",
    "address": "123 Main Street",
    "phone": "1234567890",
    "email": "alpha@clinic.com"
  },
  {
    "id": 2,
    "name": "Beta Clinic",
    "address": "456 Market Road",
    "phone": "0987654321",
    "email": "beta@clinic.com"
  }
]

POST /api/admin-panel/clinics/
Payload:
{
  "name": "Gamma Clinic",
  "address": "789 Elm St",
  "phone": "1122334455",
  "email": "gamma@clinic.com"
}

Response:
{
  "id": 3,
  "name": "Gamma Clinic",
  "address": "789 Elm St",
  "phone": "1122334455",
  "email": "gamma@clinic.com"
}

GET /api/admin-panel/clinics/{id}/
Response:
{
  "id": 1,
  "name": "Alpha Clinic",
  "address": "123 Main Street",
  "phone": "1234567890",
  "email": "alpha@clinic.com"
}

PUT /api/admin-panel/clinics/{id}/
Payload: (full update)
{
  "name": "Alpha Clinic Updated",
  "address": "123 Main St Updated",
  "phone": "1112223333",
  "email": "alpha_updated@clinic.com"
}
Response:
{
  "id": 1,
  "name": "Alpha Clinic Updated",
  "address": "123 Main St Updated",
  "phone": "1112223333",
  "email": "alpha_updated@clinic.com"
}

DELETE /api/admin-panel/clinics/{id}/
Response: 204 No Content

## Doctors
GET /api/admin-panel/doctors/
Response:
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "clinic": 1,
    "specialization": "Cardiology"
  }
]

POST /api/admin-panel/doctors/
Payload:
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "0987654321",
  "clinic": 1,
  "specialization": "Dermatology"
}

Response:
{
  "id": 2,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "0987654321",
  "clinic": 1,
  "specialization": "Dermatology"
}

GET /api/admin-panel/doctors/{id}/
PUT and DELETE similar to Clinics.


## Patients
GET /api/admin-panel/patients/
Response:
[
  {
    "id": 1,
    "first_name": "Alice",
    "last_name": "Wonder",
    "email": "alice@example.com",
    "phone": "1234567890",
    "clinic": 1,
    "dob": "1990-01-01"
  }
]

POST /api/admin-panel/patients/
{
  "first_name": "Bob",
  "last_name": "Builder",
  "email": "bob@example.com",
  "phone": "0987654321",
  "clinic": 1,
  "dob": "1985-05-10"
}
Response: same as GET for created object.

## Appointments
GET /api/admin-panel/appointments/
[
  {
    "id": 1,
    "doctor": 1,
    "patient": 1,
    "clinic": 1,
    "appointment_date": "2025-09-20",
    "appointment_time": "10:30:00",
    "status": "SCHEDULED"
  }
]

POST /api/admin-panel/appointments/
{
  "doctor": 1,
  "patient": 1,
  "clinic": 1,
  "appointment_date": "2025-09-25",
  "appointment_time": "11:00:00",
  "status": "SCHEDULED"
}

Response:
{
  "id": 2,
  "doctor": 1,
  "patient": 1,
  "clinic": 1,
  "appointment_date": "2025-09-25",
  "appointment_time": "11:00:00",
  "status": "SCHEDULED"
}

3. Clinic Dashboard

GET /api/clinic/dashboard/

Payload: None

Response:
{
  "total_doctors": 5,
  "total_patients": 120,
  "total_appointments": 80,
  "upcoming_appointments": [
    {
      "id": 1,
      "doctor": "Dr. John Doe",
      "patient": "Alice Wonder",
      "appointment_date": "2025-09-20",
      "appointment_time": "10:30:00",
      "status": "SCHEDULED"
    },
    {
      "id": 2,
      "doctor": "Dr. Jane Smith",
      "patient": "Bob Builder",
      "appointment_date": "2025-09-21",
      "appointment_time": "11:00:00",
      "status": "SCHEDULED"
    }
  ]
}

## Doctors
GET /api/clinic/doctors/

Response:
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "specialization": "Cardiology",
    "clinic": 1
  },
  {
    "id": 2,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "phone": "0987654321",
    "specialization": "Dermatology",
    "clinic": 1
  }
]

POST /api/clinic/doctors/

Payload:
{
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@example.com",
  "phone": "1122334455",
  "specialization": "Pediatrics"
}

Response:
{
  "id": 3,
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@example.com",
  "phone": "1122334455",
  "specialization": "Pediatrics",
  "clinic": 1
}

GET /api/clinic/doctors/{id}/

Response:
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "specialization": "Cardiology",
  "clinic": 1
}

PUT /api/clinic/doctors/{id}/

Payload:
{
  "first_name": "Johnathan",
  "last_name": "Doe",
  "email": "johnathan@example.com",
  "phone": "1234509876",
  "specialization": "Cardiology"
}

Response:
{
  "id": 1,
  "first_name": "Johnathan",
  "last_name": "Doe",
  "email": "johnathan@example.com",
  "phone": "1234509876",
  "specialization": "Cardiology",
  "clinic": 1
}

DELETE /api/clinic/doctors/{id}/
Response: 204 No Content

## Patients
GET /api/clinic/patients/

Response:
[
  {
    "id": 1,
    "first_name": "Alice",
    "last_name": "Wonder",
    "email": "alice@example.com",
    "phone": "1234567890",
    "dob": "1990-01-01",
    "clinic": 1
  }
]

POST /api/clinic/patients/

Payload:
{
  "first_name": "Bob",
  "last_name": "Builder",
  "email": "bob@example.com",
  "phone": "0987654321",
  "dob": "1985-05-10"
}

Response:
{
  "id": 2,
  "first_name": "Bob",
  "last_name": "Builder",
  "email": "bob@example.com",
  "phone": "0987654321",
  "dob": "1985-05-10",
  "clinic": 1
}

GET /api/clinic/patients/{id}/
Response:
{
  "id": 1,
  "first_name": "Alice",
  "last_name": "Wonder",
  "email": "alice@example.com",
  "phone": "1234567890",
  "dob": "1990-01-01",
  "clinic": 1
}

PUT /api/clinic/patients/{id}/

Payload:
{
  "first_name": "Alice",
  "last_name": "Wonders",
  "email": "alice@example.com",
  "phone": "1234567890",
  "dob": "1990-01-01"
}

Response:
{
  "id": 1,
  "first_name": "Alice",
  "last_name": "Wonders",
  "email": "alice@example.com",
  "phone": "1234567890",
  "dob": "1990-01-01",
  "clinic": 1
}

DELETE /api/clinic/patients/{id}/
Response: 204 No Content

## Appointments
GET /api/clinic/appointments/

Response:
[
  {
    "id": 1,
    "doctor": 1,
    "patient": 1,
    "clinic": 1,
    "appointment_date": "2025-09-20",
    "appointment_time": "10:30:00",
    "status": "SCHEDULED"
  }
]

POST /api/clinic/appointments/

Payload:
{
  "doctor": 1,
  "patient": 1,
  "appointment_date": "2025-09-25",
  "appointment_time": "11:00:00",
  "status": "SCHEDULED"
}

Response:
{
  "id": 2,
  "doctor": 1,
  "patient": 1,
  "clinic": 1,
  "appointment_date": "2025-09-25",
  "appointment_time": "11:00:00",
  "status": "SCHEDULED"
}

GET /api/clinic/appointments/{id}/

Response:
{
  "id": 1,
  "doctor": 1,
  "patient": 1,
  "clinic": 1,
  "appointment_date": "2025-09-20",
  "appointment_time": "10:30:00",
  "status": "SCHEDULED"
}

PUT /api/clinic/appointments/{id}/

Payload:
{
  "doctor": 1,
  "patient": 1,
  "appointment_date": "2025-09-21",
  "appointment_time": "12:00:00",
  "status": "COMPLETED"
}

Response:
{
  "id": 1,
  "doctor": 1,
  "patient": 1,
  "clinic": 1,
  "appointment_date": "2025-09-21",
  "appointment_time": "12:00:00",
  "status": "COMPLETED"
}

DELETE /api/clinic/appointments/{id}/
Response: 204 No Content

4. Doctor Dashboard

GET /api/doctor/dashboard/
Payload: None

Response:
{
  "total_consultations": 25,
  "upcoming_consultations": [
    {
      "id": 1,
      "patient": "Alice Wonder",
      "clinic": "Alpha Clinic",
      "consultation_date": "2025-09-20",
      "consultation_time": "10:30:00",
      "status": "SCHEDULED"
    },
    {
      "id": 2,
      "patient": "Bob Builder",
      "clinic": "Alpha Clinic",
      "consultation_date": "2025-09-21",
      "consultation_time": "11:00:00",
      "status": "SCHEDULED"
    }
  ]
}

## Consultations
GET /api/doctor/consultations/

Response:
[
  {
    "id": 1,
    "patient": 1,
    "clinic": 1,
    "consultation_date": "2025-09-20",
    "consultation_time": "10:30:00",
    "status": "SCHEDULED",
    "notes": "Patient has mild fever"
  },
  {
    "id": 2,
    "patient": 2,
    "clinic": 1,
    "consultation_date": "2025-09-21",
    "consultation_time": "11:00:00",
    "status": "SCHEDULED",
    "notes": "Routine check-up"
  }
]

POST /api/doctor/consultations/

Payload:
{
  "patient": 2,
  "clinic": 1,
  "consultation_date": "2025-09-25",
  "consultation_time": "14:00:00",
  "status": "SCHEDULED",
  "notes": "Follow-up consultation"
}
(doctor is automatically assigned from logged-in user)

Response:
{
  "id": 3,
  "patient": 2,
  "clinic": 1,
  "doctor": 1,
  "consultation_date": "2025-09-25",
  "consultation_time": "14:00:00",
  "status": "SCHEDULED",
  "notes": "Follow-up consultation"
}

GET /api/doctor/consultations/{id}/

Response:
{
  "id": 1,
  "patient": 1,
  "clinic": 1,
  "doctor": 1,
  "consultation_date": "2025-09-20",
  "consultation_time": "10:30:00",
  "status": "SCHEDULED",
  "notes": "Patient has mild fever"
}

PUT /api/doctor/consultations/{id}/

Payload:
{
  "patient": 1,
  "clinic": 1,
  "consultation_date": "2025-09-20",
  "consultation_time": "11:00:00",
  "status": "COMPLETED",
  "notes": "Patient prescribed medication"
}

Response:
{
  "id": 1,
  "patient": 1,
  "clinic": 1,
  "doctor": 1,
  "consultation_date": "2025-09-20",
  "consultation_time": "11:00:00",
  "status": "COMPLETED",
  "notes": "Patient prescribed medication"
}

DELETE /api/doctor/consultations/{id}/
Response: 204 No Content

## Prescriptions (nested under consultation)
GET /api/doctor/consultations/{consultation_id}/prescriptions/

Response:
[
  {
    "id": 1,
    "consultation": 1,
    "medicine": 3,
    "dosage": "500mg",
    "frequency": "2 times/day",
    "duration_days": 5,
    "notes": "Take after meals"
  },
  {
    "id": 2,
    "consultation": 1,
    "medicine": null,
    "procedure": 1,
    "notes": "X-ray examination required"
  }
]

POST /api/doctor/consultations/{consultation_id}/prescriptions/

Payload (medicine prescription):
{
  "medicine": 3,
  "dosage": "500mg",
  "frequency": "2 times/day",
  "duration_days": 5,
  "notes": "Take after meals"
}

Payload (procedure prescription):
{
  "procedure": 1,
  "notes": "X-ray examination required"
}

Response (medicine example):
{
  "id": 3,
  "consultation": 1,
  "medicine": 3,
  "dosage": "500mg",
  "frequency": "2 times/day",
  "duration_days": 5,
  "notes": "Take after meals"
}


GET /api/doctor/consultations/{consultation_id}/prescriptions/{id}/
Response:
{
  "id": 1,
  "consultation": 1,
  "medicine": 3,
  "dosage": "500mg",
  "frequency": "2 times/day",
  "duration_days": 5,
  "notes": "Take after meals"
}

PUT /api/doctor/consultations/{consultation_id}/prescriptions/{id}/
Payload:
{
  "medicine": 3,
  "dosage": "500mg",
  "frequency": "3 times/day",
  "duration_days": 7,
  "notes": "Updated dosage"
}

Response:
{
  "id": 1,
  "consultation": 1,
  "medicine": 3,
  "dosage": "500mg",
  "frequency": "3 times/day",
  "duration_days": 7,
  "notes": "Updated dosage"
}

DELETE /api/doctor/consultations/{consultation_id}/prescriptions/{id}/
Response: 204 No Content

5. Bill

1. Admin Panel Endpoints
## Material Purchase Bill

GET /admin/material-purchase/
Response:
[
  {
    "id": 1,
    "bill_number": "MPB-00001",
    "clinic": 1,
    "bill_date": "2025-09-15",
    "status": "PENDING",
    "total_amount": "1500.00",
    "supplier_name": "ABC Supplier",
    "invoice_number": "INV-1001",
    "items": [
      {
        "id": 1,
        "item_name": "Syringe",
        "quantity": 10,
        "unit_price": "50.00",
        "subtotal": "500.00"
      },
      {
        "id": 2,
        "item_name": "Gloves",
        "quantity": 20,
        "unit_price": "50.00",
        "subtotal": "1000.00"
      }
    ]
  }
]


POST /admin/material-purchase/

Payload:
{
  "clinic": 1,
  "supplier_name": "XYZ Supplier",
  "invoice_number": "INV-1002",
  "items": [
    {
      "item_name": "Mask",
      "quantity": 30,
      "unit_price": "20.00"
    }
  ]
}

Response:
{
  "id": 2,
  "bill_number": "MPB-00002",
  "clinic": 1,
  "bill_date": "2025-09-15",
  "status": "PENDING",
  "total_amount": "600.00",
  "supplier_name": "XYZ Supplier",
  "invoice_number": "INV-1002",
  "items": [
    {
      "id": 3,
      "item_name": "Mask",
      "quantity": 30,
      "unit_price": "20.00",
      "subtotal": "600.00"
    }
  ]
}

## Clinic Bill

GET /admin/clinic-bill/

Response:
[
  {
    "id": 1,
    "bill_number": "CB-00001",
    "clinic": 1,
    "bill_date": "2025-09-15",
    "status": "PAID",
    "total_amount": "2000.00",
    "vendor_name": "Vendor A",
    "items": [
      {
        "id": 1,
        "item_name": "Medical Equipment",
        "quantity": 2,
        "unit_price": "1000.00",
        "subtotal": "2000.00"
      }
    ]
  }
]

POST /admin/clinic-bill/

Payload:
{
  "clinic": 1,
  "vendor_name": "Vendor B",
  "items": [
    {
      "item_name": "Stethoscope",
      "quantity": 5,
      "unit_price": "300.00"
    }
  ]
}

Response:
{
  "id": 2,
  "bill_number": "CB-00002",
  "clinic": 1,
  "bill_date": "2025-09-15",
  "status": "PENDING",
  "total_amount": "1500.00",
  "vendor_name": "Vendor B",
  "items": [
    {
      "id": 2,
      "item_name": "Stethoscope",
      "quantity": 5,
      "unit_price": "300.00",
      "subtotal": "1500.00"
    }
  ]
}

## Lab Bill

GET /admin/lab-bill/

Response:
[
  {
    "id": 1,
    "bill_number": "LB-00001",
    "clinic": 1,
    "bill_date": "2025-09-15",
    "status": "PENDING",
    "total_amount": "1200.00",
    "lab_name": "LabCorp",
    "work_description": "Blood tests",
    "items": [
      {
        "id": 1,
        "test_or_service": "Blood Sugar",
        "cost": "200.00"
      },
      {
        "id": 2,
        "test_or_service": "CBC",
        "cost": "1000.00"
      }
    ]
  }
]

POST /admin/lab-bill/

Payload:
{
  "clinic": 1,
  "lab_name": "QuickLab",
  "work_description": "Routine blood work",
  "items": [
    {
      "test_or_service": "Cholesterol",
      "cost": "500.00"
    }
  ]
}

Response:
{
  "id": 2,
  "bill_number": "LB-00002",
  "clinic": 1,
  "bill_date": "2025-09-15",
  "status": "PENDING",
  "total_amount": "500.00",
  "lab_name": "QuickLab",
  "work_description": "Routine blood work",
  "items": [
    {
      "id": 3,
      "test_or_service": "Cholesterol",
      "cost": "500.00"
    }
  ]
}

## Pharmacy Bill

GET /admin/pharmacy-bill/

Response:
[
  {
    "id": 1,
    "bill_number": "PB-00001",
    "clinic": 1,
    "bill_date": "2025-09-15",
    "status": "PAID",
    "total_amount": "800.00",
    "patient": 1,
    "items": [
      {
        "id": 1,
        "item_type": "MEDICINE",
        "medicine": 1,
        "procedure": null,
        "quantity": 2,
        "unit_price": "200.00",
        "subtotal": "400.00"
      },
      {
        "id": 2,
        "item_type": "PROCEDURE",
        "medicine": null,
        "procedure": 1,
        "quantity": 1,
        "unit_price": "400.00",
        "subtotal": "400.00"
      }
    ]
  }
]

POST /admin/pharmacy-bill/

Payload:
{
  "clinic": 1,
  "patient": 2,
  "items": [
    {
      "item_type": "MEDICINE",
      "medicine": 3,
      "quantity": 2
    },
    {
      "item_type": "PROCEDURE",
      "procedure": 2
    }
  ]
}

Response:
{
  "id": 2,
  "bill_number": "PB-00002",
  "clinic": 1,
  "bill_date": "2025-09-15",
  "status": "PENDING",
  "total_amount": "1200.00",
  "patient": 2,
  "items": [
    {
      "id": 3,
      "item_type": "MEDICINE",
      "medicine": 3,
      "procedure": null,
      "quantity": 2,
      "unit_price": "300.00",
      "subtotal": "600.00"
    },
    {
      "id": 4,
      "item_type": "PROCEDURE",
      "medicine": null,
      "procedure": 2,
      "quantity": 1,
      "unit_price": "600.00",
      "subtotal": "600.00"
    }
  ]
}

2. Clinic Panel Endpoints

Example: POST /clinic/material-purchase/

Payload:
{
  "supplier_name": "XYZ Supplier",
  "invoice_number": "INV-1002",
  "items": [
    {
      "item_name": "Mask",
      "quantity": 30,
      "unit_price": "20.00"
    }
  ]
}

Response:
{
  "id": 2,
  "bill_number": "MPB-00002",
  "clinic": 1,   // auto-filled from logged-in clinic
  "bill_date": "2025-09-15",
  "status": "PENDING",
  "total_amount": "600.00",
  "supplier_name": "XYZ Supplier",
  "invoice_number": "INV-1002",
  "items": [
    {
      "id": 3,
      "item_name": "Mask",
      "quantity": 30,
      "unit_price": "20.00",
      "subtotal": "600.00"
    }
  ]
}
All other clinic endpoints (Clinic Bill, Lab Bill, Pharmacy Bill) follow the same pattern