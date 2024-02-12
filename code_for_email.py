import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_notification(receiver_email, subject, body):
    # Set up the email parameters
    sender_email = "your_email@gmail.com"
    password = "your_password"
    
    # Create a message object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    # Add the body to the email
    message.attach(MIMEText(body, "plain"))
    
    # Connect to the SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    
    # Log in to the email server
    server.login(sender_email, password)
    
    # Send the email
    server.sendmail(sender_email, receiver_email, message.as_string())
    
    # Close the connection to the SMTP server
    server.quit()

# Example usage
receiver_email = "recipient_email@example.com"
subject = "Notification"
body = "This is a notification email."

send_email_notification(receiver_email, subject, body)
