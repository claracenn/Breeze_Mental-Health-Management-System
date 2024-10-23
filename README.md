
# Breeze - A Mental Health Management System

## Overview

This project is a Python-based command-line application for managing mental health communication and support. It includes functionality for three types of users: Admin, Mental Health and Wellbeing Practitioners (MHWPs), and Patients. The project is designed with modularity and extendability in mind, providing basic features such as user management, appointment booking, mood tracking, journaling, and data persistence.

## Features

### Admin
- Allocate patients to MHWPs.
- Edit MHWP or patient records.
- Delete MHWP or patient records.
- Disable MHWP or patient records (can login/logout but no change can be made).
- Display a summary of patients, MHWPs, and their related appointments.

### Patients
- Edit personal information (name, email, emergency contact).
- Track daily mood with a color code system and add comments.
  <img width="383" alt="image" src="https://github.com/user-attachments/assets/d28b5f55-82f1-4dbe-8837-28a62902ff09">
- Add daily journal entries and save with latest date/time.
- Access meditation and relaxation exercises based on keyword search.
- Book and cancel appointments with their assigned MHWP.
- Receive email notifications for booking confirmations or cancellations.

### MHWPs (Mental Health and Wellbeing Practitioners)
- View their calendar with requested and confirmed appointments.
- Confirm or cancel appointments, and send email notifications to patient.
- Add patient information (conditions, notes, etc. which can be selected from predefined list)
- View patient data on a dashboard with mood tracking charts.

## Project Structure

```
/breeze_mental_health_system
    /data          # Persistent storage for user and appointment data (JSON/SQLite).
    /models        # Data models for users and appointments.
    /controllers   # Controllers that manage Admin, Patient, and MHWP functionality.
    /utils         # Utility functions such as email notifications and validation.
    main.py        # Main entry point of the application.
```

### Models
- **User**: Base class for Admin, Patients, and MHWPs.
- **Admin**: Inherits from User and manages system-wide operations.
- **Patient**: Inherits from User, tracks mood and journal entries, and books appointments.
- **MHWP**: Inherits from User and manages patient appointments and records.
- **Appointment**: Represents an appointment between a patient and an MHWP.

### Controllers
- **AdminController**: Manages admin operations such as user allocation, editing, and displaying summaries.
- **PatientController**: Manages patient-specific functionality like mood tracking, journaling, and appointment booking.
- **MHWPController**: Manages MHWP-specific functionality like confirming appointments and managing patient records.

### Utilities
- **notifications.py**: Provides a simple interface for sending email notifications.
- **validation.py**: Validates user input and ensures data integrity.

### Persistence
- **Storage**: Provides methods to save and load data persistently using JSON.

## How to Run the Application

1. Clone the repository or download the ZIP file.
2. Navigate to the project directory and run `main.py` using Python:
   ```bash
   python main.py
   ```
3. Follow the command-line prompts to interact with the system.

## Contributions

## License
