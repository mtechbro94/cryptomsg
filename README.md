# Secure Data Retrieval System - Modern Rewrite

A modern, production-ready Django application for secure data retrieval with end-to-end encryption, certificate-based authentication, and role-based access control.

## 🚀 Features

### Security
- **End-to-End Encryption** - All messages encrypted using Fernet (AES-256)
- **Digital Certificates** - Cloud Authority can issue certificates for verified messages
- **Audit Logging** - Complete message history and tracking
- **Password Security** - Strong password validation (8+ chars, uppercase, digits)

### User Roles
1. **Cloud Authority (CA)** - Issues digital certificates and validates messages
2. **Router** - Accepts messages and forwards them to CA for certification
3. **Publisher** - Publishes encrypted messages
4. **User** - Send and receive encrypted messages

### Modern Architecture
- Clean separation of concerns (Models, Views, Forms, Templates)
- Django ORM with proper database relationships
- Bootstrap 5 responsive UI
- RESTful API endpoints
- Comprehensive error handling

## 📋 Project Structure

```
SecureMessenger/
├── app/
│   ├── models.py          # UserProfile, Message, MessageLog, Certificate
│   ├── views.py           # Clean, modular view functions
│   ├── urls.py            # Modern URL routing
│   ├── forms.py           # Django form validation
│   ├── admin.py           # Admin panel configuration
│   └── migrations/        # Database migrations
├── templates/
│   ├── base.html          # Base template with Bootstrap 5
│   ├── home.html          # Landing page
│   ├── auth/              # Login/Register pages
│   ├── dashboard/         # Role-based dashboards
│   ├── messages/          # Message views
│   ├── router/            # Router operations
│   └── ca/                # Cloud Authority operations
├── static/
│   ├── css/
│   └── js/
├── manage.py              # Django management script
├── Requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.11.9
- pip
- Virtual Environment

### Installation Steps

1. **Navigate to the project directory:**
   ```bash
   cd "d:\user\Downloads\IV year MiniProject\Secure data Retrieval Project\MPNS04\MPNS04PROJECT"
   ```

2. **Activate virtual environment:**
   ```bash
   .\.venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r Requirements.txt
   ```

4. **Run migrations (already done):**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin panel):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Home: http://127.0.0.1:8000
   - Admin Panel: http://127.0.0.1:8000/admin

## 👥 Test Accounts

Create accounts through the registration form with any username and password meeting the requirements:
- **Password Requirements:** 8+ characters, 1 uppercase letter, 1 digit

## 📱 URL Routes

### Public Routes
- `/` - Home page
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout

### Authenticated Routes
- `/dashboard/` - Role-based dashboard
- `/send/` - Send a new message
- `/inbox/` - View received messages
- `/outbox/` - View sent messages
- `/message/<int:message_id>/` - View message details

### Router Routes
- `/router/accept/<int:message_id>/` - Accept message and forward to CA

### Cloud Authority Routes
- `/ca/certificate/<int:message_id>/` - Create digital certificate for message

### API Endpoints
- `/api/message/<int:message_id>/status/` - Get message status (JSON)
- `/api/stats/` - Get user statistics (JSON)

## 🗄️ Database Models

### UserProfile
- Extends Django User model
- Stores user role (CA, Router, Publisher, User)
- Organization field for metadata

### Message
- sender, receiver (ForeignKey to User)
- subject, encrypted_content
- encryption_key (Fernet key)
- status (DRAFT, SENT, ROUTER_ACCEPTED, CERTIFICATE_CREATED, DELIVERED, REJECTED)
- certificate (CA signature)
- Audit trail with timestamps

### MessageLog
- Audit log for message operations
- Tracks who performed what action and when
- Supports different log types (CREATE, SEND, ACCEPT, CERTIFICATE, DELIVER, REJECT)

### Certificate
- Issued by Cloud Authority
- Links to Message
- Contains certificate data and validity period

## 🔐 Encryption Details

Messages are encrypted using **Fernet (symmetric encryption)** from the `cryptography` library:
- Algorithm: AES-128 in CBC mode
- HMAC: SHA256 for authentication
- Token Format: Base64 encoded

**Encryption Flow:**
1. User composes message
2. System generates random Fernet key
3. Message encrypted with key
4. Both stored in database separately
5. Only authorized users can decrypt with their key

## 🌐 User Workflows

### Regular User Sending a Message
```
User writes message → Message encrypted → Status: SENT → Router accepts → CA certifies → Recipient receives
```

### Router Accepting a Message
```
Dashboard shows pending messages → Router reviews → Clicks "Accept" → Message forwarded to CA
```

### Cloud Authority Certifying
```
Dashboard shows pending certificates → CA reviews decrypted content → Issues certificate → Message marked as certified
```

## 📊 Admin Panel

Access the Django admin panel at `/admin/`:
- Manage users and profiles
- View all messages
- Monitor message logs
- Manage certificates
- User role assignment

## 🐛 Troubleshooting

### Server won't start
- Ensure virtual environment is activated
- Run migrations: `python manage.py migrate`
- Check Python version: `python --version` (should be 3.11.9)

### Database errors
- Delete `db.sqlite3` and run migrations again
- Check migrations folder for conflicting files

### Template not found
- Ensure template files are in correct folders
- Clear Django cache: Delete `__pycache__` folders

### Permission denied
- Check user role permissions
- Ensure user is authenticated
- Verify database has UserProfile records

## 📦 Dependencies

- **Django 4.2.5** - Web framework
- **cryptography 41.0.3** - Encryption library
- **mysql-connector-python** - MySQL support (optional)
- **Pillow 10.0.0** - Image processing

## 🎨 UI Features

- **Responsive Design** - Mobile-friendly with Bootstrap 5
- **Dark Navigation Bar** - Professional appearance
- **Status Badges** - Color-coded message statuses
- **Role Badges** - Visual distinction between user roles
- **Toast Notifications** - Auto-dismissing alerts
- **Pagination** - Efficient message browsing

## 🔍 What Changed from Original

✅ **Removed:**
- Hardcoded MySQL connection in views
- Old template structure (base1.html, base2.html, etc.)
- Direct SQL queries
- Unsecured database configuration

✅ **Added:**
- Proper Django Models (ORM)
- Django Forms with validation
- Modern Bootstrap 5 UI
- Role-based dashboards
- Audit logging system
- API endpoints
- Authentication system
- Clean code organization
- Security best practices

## 🚀 Next Steps

1. **Create test accounts** via registration page
2. **Test message flow** (User → Router → CA)
3. **Monitor audit logs** in admin panel
4. **Customize styling** if needed in `templates/base.html`
5. **Deploy to production** (configure ALLOWED_HOSTS, DEBUG=False, HTTPS, etc.)

## 📝 Notes

- This is a development version. For production, update security settings in `settings.py`
- Database uses SQLite. For production, switch to PostgreSQL or MySQL
- Static files need to be collected: `python manage.py collectstatic`
- Enable CSRF protection and HTTPS in production

## 🤝 Support

For issues or questions about the new architecture, refer to the code comments or Django documentation.

---

**Version:** 2.0 (Completely Rewritten)
**Last Updated:** February 12, 2026
