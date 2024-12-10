# MHWP TABLES

-   **MHWP Table**: List of MHWPs in the system.
-   **Appointment Table**: Records appointments between Patients and MHWPs.
-   **Patient Record Table**: Keeps track of Patients’ conditions.
-   **Mood Log Table**: Logs Patients’ mood entries for access by MHWPs.

## 1. **MHWP Table**

**MHWP** table keeps track of all MHWPs with their email and Patient list.

### Fields:

-   `mhwp_id` [PK; FK->User/user_id]: Unique identifier for each MHWP.
-   `name`: Name of MHWP.
-   `email`: Email id of MHWPs for sending notifications.
-   `patient_ids`[FK->patient_id]: List of patients for each MHWP.

## 2. **Appointment Table**

**Appointment** table stores information about the time of each appointment with MHWPs and the current status.

### Fields:

-   `appointment_id` [PK]: Unique identifier for each appointment.
-   `patient_id` [FK->Patient/patient_id]: References the patient booking the appointment.
-   `mhwp_id` [FK->MHWP]: References the assigned MHWP for this appointment.
-   `date`: Date of the appointment.
-   `time_slot`: Time slot of the appointment.
-   `status` (ENUM): `PENDING`, `CONFIRMED`, `CANCELLED`
-   `notes`: Additional information about the appointment.
-   `create_time`: Time of appointment creation.
-   `last_updated`: Time of the latest update.

## 3. **Patient Record Table**

**Patient Record** table keeps track of patients’ conditions and additional notes.

### Fields:

-   `patient_id` [PK]: Unique identifier for each patient record.
-   `condition`: Patient’s mental health condition.
-   `notes`: Additional information about the patient.

## 4. **Mood Log Table**

**Mood Log** table allows patients to update their mood daily and add comments, accessible by MHWPs on their dashboard.

### Fields:

-   `patient_id` [Composite PK; FK->Patient/patient_id]: References the patient table for patient info.
-   `date` [Composite PK]: Date of the mood entry.
-   `mood_color`: Color-coded representation of the mood (e.g., green for positive, red for negative).
-   `mood_comments`: Text field where the patient can add comments about their mood.
