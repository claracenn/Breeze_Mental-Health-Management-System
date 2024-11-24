import smtplib

port = 587
smtp_server = "smtp.gmail.com"
sender_email = "breeze.app.user@gmail.com"

# gmail email = "breeze.app.user@gmail.com"
# gmail password = "breeze@123"

# app specific password for google stmp under key python_email
password = "cwog byoy wrqn xlhu"




def send_email(recipient_email, subject, body):
    """
    Parameter: Type
    recipient_email: string
    subject: string
    body: string
    
    Functionality:
        Sends and email from "breeze.app.user@gmail.com" to the recipient email

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Raises:
        smtplib.SMTPException: If an error occurs during the email sending process.

    
    Example:
    recipient_email = "arkash707@gmail.com"
    subject = "Your Appointment has been confirmed"
    message_body = '''Testing New Email\n
        Hello World\n Hello World\n
        Breeze Mental Health and Wellbeing App
    '''
    send_email(recipient_email, subject, message_body)

    """

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            complete_email = f"Subject: {subject}\n\n{body}"
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, complete_email)
            return True
    except Exception as error:
        print("Failed to send email")
        print(f"Error: ${error}")
        return False

