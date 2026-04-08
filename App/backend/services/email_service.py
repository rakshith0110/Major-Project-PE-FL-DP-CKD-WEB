"""
Email notification service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from backend.core.database import get_db_connection

# Email configuration (update with actual SMTP settings)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"  # Update this
SMTP_PASSWORD = "your-app-password"  # Update this
FROM_EMAIL = "your-email@gmail.com"  # Update this

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create HTML version
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; padding: 20px;">
                        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                            🏥 Federated Learning CKD System
                        </h2>
                        <div style="margin: 20px 0; line-height: 1.6;">
                            {message}
                        </div>
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 12px;">
                            <p>This is an automated notification from the Federated Learning CKD System.</p>
                            <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML
            html_part = MIMEText(html_message, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            # Log to database
            self._log_email(to_email, subject, message, 'sent')
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            self._log_email(to_email, subject, message, 'failed')
            return False
    
    def _log_email(self, to_email: str, subject: str, message: str, status: str):
        """Log email to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO email_notifications 
                (recipient_email, subject, message, status, sent_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (to_email, subject, message, status))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log email: {str(e)}")
    
    def notify_admin_training_complete(self, client_name: str, accuracy: float, 
                                      admin_email: str):
        """Notify admin when client completes training"""
        subject = f"🎯 Training Complete - {client_name}"
        message = f"""
        <p><strong>Client Training Completed</strong></p>
        <p>Client <strong>{client_name}</strong> has successfully completed model training.</p>
        <ul>
            <li><strong>Accuracy:</strong> {accuracy:.2%}</li>
            <li><strong>Status:</strong> New Update Available</li>
            <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
        <p>The client's model weights are ready for aggregation.</p>
        <p>Please log in to the admin dashboard to perform aggregation.</p>
        """
        return self.send_email(admin_email, subject, message)
    
    def notify_client_aggregation_complete(self, client_email: str, 
                                          round_number: int, 
                                          global_accuracy: Optional[float] = None):
        """Notify client when aggregation is complete"""
        subject = f"✅ Global Model Updated - Round {round_number}"
        message = f"""
        <p><strong>Aggregation Completed</strong></p>
        <p>The global model has been updated in round <strong>{round_number}</strong>.</p>
        """
        
        if global_accuracy:
            message += f"""
            <ul>
                <li><strong>Global Accuracy:</strong> {global_accuracy:.2%}</li>
            </ul>
            """
        
        message += """
        <p>The updated global model is now available for predictions in your dashboard.</p>
        <p>You can continue training with the new global model as the starting point.</p>
        """
        return self.send_email(client_email, subject, message)
    
    def notify_client_created(self, client_email: str, client_name: str, 
                             login_password: str, training_password: str):
        """Notify new client with credentials"""
        subject = "🔐 Your Federated Learning CKD Account"
        message = f"""
        <p><strong>Welcome to Federated Learning CKD System</strong></p>
        <p>Your account has been created successfully.</p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <p><strong>Login Credentials:</strong></p>
            <ul>
                <li><strong>Client Name:</strong> {client_name}</li>
                <li><strong>Login Password:</strong> {login_password}</li>
                <li><strong>Training Password:</strong> {training_password}</li>
            </ul>
        </div>
        <p><strong>⚠️ Important:</strong></p>
        <ul>
            <li>Use the <strong>Login Password</strong> to access your dashboard</li>
            <li>Use the <strong>Training Password</strong> to authorize model training</li>
            <li>Keep these credentials secure and do not share them</li>
        </ul>
        <p>Please change your passwords after first login.</p>
        """
        return self.send_email(client_email, subject, message)
    
    def notify_training_started(self, client_email: str, client_name: str, 
                               epochs: int, batch_size: int):
        """Notify client when training starts"""
        subject = f"🚀 Training Started - {client_name}"
        message = f"""
        <p><strong>Model Training Initiated</strong></p>
        <p>Your local model training has started with the following configuration:</p>
        <ul>
            <li><strong>Epochs:</strong> {epochs}</li>
            <li><strong>Batch Size:</strong> {batch_size}</li>
        </ul>
        <p>You will receive another notification when training is complete.</p>
        <p>You can monitor the progress in your dashboard.</p>
        """
        return self.send_email(client_email, subject, message)

# Create singleton instance
email_service = EmailService()

# Made with Bob
