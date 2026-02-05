import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.utils import DNS_NAME


class CustomEmailBackend(EmailBackend):
    """
    Custom email backend that handles SSL certificate verification issues
    """
    
    def open(self):
        """
        Opens a connection to the email server with custom SSL configuration
        """
        if self.connection:
            return False
        
        try:
            # Create SSL context with relaxed verification for development
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect to SMTP server
            self.connection = smtplib.SMTP(self.host, self.port, 
                                          local_hostname=DNS_NAME.get_fqdn(),
                                          timeout=self.timeout)
            
            if self.use_tls:
                # Start TLS with custom SSL context
                self.connection.starttls(context=context)
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
    
    def close(self):
        """Closes the connection to the email server."""
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except smtplib.SMTPServerDisconnected:
                # This happens when the connection is already closed
                self.connection.close()
            finally:
                self.connection = None
        except Exception:
            if not self.fail_silently:
                raise
