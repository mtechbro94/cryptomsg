from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import json


class UserRole(models.TextChoices):
    """User role choices"""
    CLOUD_AUTHORITY = 'CA', 'Cloud Authority'
    ROUTER = 'ROUTER', 'Router'
    PUBLISHER = 'PUBLISHER', 'Publisher'
    USER = 'USER', 'User'


class UserProfile(models.Model):
    """Extended user profile with roles"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    organization = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Message(models.Model):
    """Secure message model"""
    MESSAGE_STATUS = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ROUTER_ACCEPTED', 'Router Accepted'),
        ('CERTIFICATE_CREATED', 'Certificate Created'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    encrypted_content = models.TextField()  # Encrypted message content
    encryption_key = models.TextField(blank=True)  # Fernet key (base64 encoded)
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS, default='DRAFT')
    certificate = models.TextField(blank=True, null=True)  # CA signature
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['receiver', 'status']),
        ]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    def encrypt_content(self, content):
        """Encrypt message content"""
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(content.encode('utf-8'))
        self.encryption_key = key.decode('utf-8')
        self.encrypted_content = encrypted.decode('utf-8')

    def decrypt_content(self):
        """Decrypt message content"""
        try:
            if not self.encryption_key:
                return None
            cipher = Fernet(self.encryption_key.encode('utf-8'))
            decrypted = cipher.decrypt(self.encrypted_content.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            return f"Error decrypting: {str(e)}"


class MessageLog(models.Model):
    """Audit log for message operations"""
    LOG_TYPE = [
        ('CREATE', 'Created'),
        ('SEND', 'Sent'),
        ('ACCEPT', 'Accepted by Router'),
        ('CERTIFICATE', 'Certificate Created'),
        ('DELIVER', 'Delivered'),
        ('REJECT', 'Rejected'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_log_type_display()} - {self.message}"


class Certificate(models.Model):
    """Digital certificate issued by CA"""
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='cert')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    certificate_data = models.TextField()  # Digital signature/certificate
    issued_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Certificate for Message {self.message.id}"
