# PATIENT TABLES

- **User Table**: General user information (applies to all user types).
- **Patient Info Table**: Patient-specific details, including the assigned MHWP.
- **Patient Journal Table**: Stores personal journal entries.
- **Appointment Table**: Records appointments between Patients and MHWPs.
- **Exercise Resource Table**: Provides relaxation and meditation exercises.


## 1. **User Table**

**User** table stores general information for all types of users in the system (Admin, Patient, and MHWP). 

### Fields:

- `user_id` [PK]: Unique identifier for each user.
- `username`: Login name for the user.
- `password`: Password for authentication (empty).
- `role` (ENUM): `admin`, `mhwp`, `patient`
- `status`(ENUM): `ACTIVE`, `DISABLED`


## 2. **Patient Info Table**

**Patient** table stores specific information about each patient.

### Fields:

- `patient_id` [PK; FK->User/user_id]: Unique identifier for each patient.
- `name`: Name of the patient.
- `email`: Contact email for the patient.
- `emergency_contact_email`: Email of the emergency contact.
- `mhwp_id` [FK->MHWP]: References the assigned MHWP for this patient.


## 3. **Patient Journal Table**

**Mood Log** records daily mood entries for patients. 

### Fields:

- `patient_id` [Composite PK; FK->Patient/patient_id]: References the patient table for patient info.
- `date` [Composite PK]: Latest date of saving the mood entry.
- `mood_color`: Color-coded representation of the mood (e.g., green for positive, red for negative).
- `mood_comments`: Text field where the patient can add comments about their mood.
- `journal_text`: Text content of the journal entry.


## 4. **Appointment Table**

**Appointment** table stores information about the time of each appointment with MHWPs and the current status.

### Fields:

- `appointment_id` [PK]: Unique identifier for each appointment.
- `patient_id` [FK->FK->Patient/patient_id]: References the patient booking the appointment.
- `mhwp_id` [FK->MHWP]: References the assigned MHWP for this appointment.
- `date_time`: Date and time of the appointment.
- `status`(ENUM): `BOOKED`, `CONFIRMED`, `CANCELED`
- `notes`: Additional information about the appointment.


## 5. **Exercise Resource Table**

**Exercise Resource** table stores links to relaxation and meditation exercises that patients can access. 

### Fields:

- `resource_id` [PK]: Unique identifier for each resource.
- `title`: Title of the exercise or resource.
- `description`: Brief description of the resource.
- `url`: URL link to the exercise (audio or video).
