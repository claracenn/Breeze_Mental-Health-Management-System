
# Breeze - A Mental Health Management System

## Overview

This project is a Python-based command-line application for managing mental health communication and support. It includes functionality for three types of users: Admin, Mental Health and MHWPs, and Patients. The project is designed with modularity and extendability in mind, providing features such as user management, appointment booking, mood tracking, journaling, and so on.

## Features

### Admin
- Allocate patients to MHWPs.
- Resolve patients' requests of changing MHWP.
- Edit MHWP or patient records.
- Disable or enable user accounts.
- Delete MHWP or patient records.
- Display a summary of patients, MHWPs, and their related appointments.

### Patients
- View and edit personal profile.
- View, add, edit and delete daily journal entries.
- View, add, edit and delete daily mood and comments.
- View, make, and cancel appointments with MHWP.
- Access meditation and relaxation exercises based on keyword search.
- View recommended resources provided by the patient's MHWP.
- Provide feedback to appointments.
- Receive email notifications for booking confirmations or cancellations.

### MHWPs (Mental Health and Wellbeing Practitioners)
- View calendar with requested and confirmed appointments.
- Confirm or cancel appointments, and send email notifications to patient.
- Suggest related resources to patients.
- View feedback from patients on appointments.
- View and update patient's dashboard with mood tracking charts.
- Email patient's emergency contact.

## Project Structure

```
/breeze_mental_health_system
    /controllers   # Controllers that manage Admin, Patient, and MHWP functionality.
    /data          # Storage for user and appointment data (JSON).
    /models        # Data models for users and appointments.
    /utils         # Utility functions including data handling, email notifications, and display.
    main.py        # Main entry point of the application.
```

### Models
- **User**: Base class for Admin, Patients, and MHWPs.
- **Admin**: Inherits from User. Represents system administrators who manage system-wide operations.
- **Patient**: Inherits from User. Represents patients using the system.
- **MHWP**: Inherits from User. Represents practitioners managing patient appointments and records.

### Controllers
- **AdminController**: Manages admin operations such as user allocation, editing, and displaying summaries.
- **PatientController**: Manages patient-specific functionality like mood tracking, journaling, and appointment booking.
- **MHWPController**: Manages MHWP-specific functionality like user management.

### Utilities
- **email_helper.py**: Provides functionality to send email notifications using Gmail SMTP. Supports sending custom messages to recipients for alerts and updates.
- **data_handler.py**: Contains functions to handle JSON data operations, including reading, writing, updating, and deleting entries. Also includes utilities for sanitizing input data and creating formatted tables for display using pandas.
- **display_manager.py**: Manages user interface elements like menus and navigation breadcrumbs. Provides methods for printing styled messages, dividers, and menus, with a focus on improving user interaction.

## How to Run the Application
1. Clone the repository https://github.com/claracenn/Breeze_Mental-Health-Management-System.git or download the ZIP file.
2. Navigate to the project directory and run `main.py` using Python:
   ```bash
   python main.py
   ```
3. Follow the command-line prompts to interact with the system.

## Contributions
<p => <a href="https://github.com/timothysim"> <img src="https://github.com/timothysim.png?size=100" width="40" height="40" alt="Rachel Seah Yan Ting" /> </a> <a href="https://github.com/racheiii"> <img src="https://github.com/racheiii.png?size=100" width=40" height="40" alt="Timothy Sim Mong Wei" /> </a> <a href="https://github.com/TrashP"> <img src="https://github.com/TrashP.png?size=100" width="40" height="40" alt="Arnb Goswami" /> </a> <a href="https://github.com/arkash55"> <img src="https://github.com/arkash55.png?size=100" width="40" height="40" alt="Arkash Vijayakumar" /> </a> <a href="https://github.com/claracenn"> <img src="https://github.com/claracenn.png?size=100" width="40" height="40" alt="Baihui Cen" /> </a> <a href="https://github.com/mawenxin01"> <img src="https://github.com/mawenxin01.png?size=100" width="40" height="40" alt="Wenxin Ma" /> </a> <a href="https://github.com/JasmineSong666"> <img src="https://github.com/JasmineSong666.png?size=100" width="40" height="40" alt="Jasmine Song" /> </a> </p>

**Admin functions developers**:
- [Rachel Seah Yan Ting](https://github.com/timothysim)
- [Timothy Sim Mong Wei](https://github.com/racheiii)

**MHWP functions developers**:
- [Arnb Goswami](https://github.com/TrashP)
- [Arkash Vijayakumar](https://github.com/arkash55)

**Patient functions developers**:
- [Baihui Cen](https://github.com/claracenn)
- [Wenxin Ma](https://github.com/mawenxin01)
- [Jasmine Song](https://github.com/JasmineSong666)


