# Employee Attendance Management System

A Django-based web application for tracking employee attendance, managing user registrations, and monitoring task submissions with an intuitive admin dashboard.

## 📋 Features

### 🔐 **Authentication System**
- User Registration with validation
- Secure Login/Logout functionality
- Role-based access control (Admin & Regular Users)
- Password protection and security

### 📅 **Attendance Tracking**
- Automatic daily login time recording
- Interactive calendar view with monthly navigation
- Attendance status visualization (Present/Absent/Future)
- Database-backed record storage
- Unique daily attendance records per user
- Real-time login time timestamp

### 📝 **Task Management**
- Users can create and submit tasks/notes
- Dashboard view of all submissions
- Chronological sorting (newest first)
- User-specific submission tracking

### 👨‍💼 **Admin Dashboard** (In Progress)
- Comprehensive attendance reports
- User and submission management
- Date range filtering
- Export functionality (CSV/PDF)
- User-based filtering

## 🛠️ Tech Stack

- **Backend:** Django 4.2.7
- **Database:** SQLite3 (Development), PostgreSQL (Production)
- **Frontend:** HTML5, CSS3, Bootstrap
- **Language:** Python 3.x
- **Authentication:** Django built-in auth system

## 📁 Project Structure

```
Employee-Attendance/
├── auth/                           # Main Django project
│   ├── settings.py                # Django settings
│   ├── urls.py                    # URL configuration
│   ├── wsgi.py                    # WSGI application
│   └── asgi.py                    # ASGI application
├── myapp/                         # Main Django app
│   ├── models.py                  # Database models
│   ├── views.py                   # View functions
│   ├── urls.py                    # App URLs
│   ├── admin.py                   # Admin configuration
│   ├── migrations/                # Database migrations
│   └── templates/                 # HTML templates
│       ├── register.html          # Registration page
│       ├── login.html             # Login page
│       ├── dashboard.html         # User dashboard
│       ├── calendar.html          # Attendance calendar
│       ├── submission.html        # Task submission form
│       └── admin_dashboard.html   # Admin panel
├── static/                        # Static files (CSS, JS)
├── manage.py                      # Django management
├── requirements.txt               # Dependencies
├── db.sqlite3                     # SQLite database
└── README.md                      # This file
```

## 🗄️ Database Models

### UserAttendance
```
- user (ForeignKey) - Link to User
- date (DateField) - Attendance date
- login_time (TimeField) - Login time
- status (CharField) - Present/Absent/Future
- unique_together (user, date) - One record per user per day
```

### Submission
```
- user (ForeignKey) - Link to User
- text (CharField) - Submission content
- created_at (DateTimeField) - Auto timestamp
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Clone Repository
```bash
git clone https://github.com/Nandoliya-Shoeb/Employee-Attendance-Management-System.git
cd Employee-Attendance
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Enter username, email, and password
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Server will be running at: `http://127.0.0.1:8000/`

## 📖 Usage

### For Regular Users
1. **Register:** Go to `/register` and create an account
2. **Login:** Use credentials to login at `/login`
3. **View Attendance:** Access calendar at `/calendar` (auto-records login)
4. **Submit Tasks:** Go to `/submission` to add notes/tasks
5. **View Dashboard:** Check all submissions in dashboard

### For Admin Users
1. Login with superuser account
2. Access Admin Panel at `/admin-dashboard`
3. View all attendance records and submissions
4. Filter by date range and user
5. Export reports (CSV/PDF)

## 🔑 Key Functionality

### Auto Attendance Recording
The system automatically records attendance when a user visits the calendar page:
```python
UserAttendance.objects.get_or_create(
    user=request.user,
    date=today,
    defaults={"login_time": datetime.now().time(), "status": "present"}
)
```

### Role-Based Routing
```
Admin Login → Admin Dashboard
Regular User Login → User Dashboard
```

### Calendar Navigation
- Select month and year from dropdown
- View attendance status for all days
- Display login time for marked days

## 🔒 Security Features

- Django CSRF protection
- Secure password hashing
- Login required decorators on protected views
- User-specific data isolation
- Session-based authentication

## 📊 Admin Panel Features (Partial)

- View all submissions with pagination
- Filter attendance by user and date range
- Prepare for CSV and PDF export functionality
- User management and filtering

## ⚙️ Configuration

### Edit settings.py
- Database configuration
- Static files location
- Allowed hosts
- Debug mode (set to False in production)

### Environment Variables (Production)
```
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
```

## 🚀 Deployment

### Railway Deployment
1. Push code to GitHub
2. Create Railway account at railway.app
3. Select "Deploy from GitHub"
4. Configure environment variables
5. Railway auto-deploys on push

### Heroku Deployment
1. Create Procfile and requirements.txt ✅
2. Create Heroku account
3. Push to Heroku git
4. Configure database

## 🐛 Troubleshooting

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Database Lock Error
```bash
rm db.sqlite3
python manage.py migrate
```

## 📝 Future Enhancements

- [ ] Complete Admin Dashboard with reports
- [ ] CSV/PDF export functionality
- [ ] Email notifications for attendance
- [ ] Mobile responsive improvements
- [ ] API endpoints (REST API)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Bulk attendance import
- [ ] Shift management
- [ ] Leave management system

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Shoeb Nandoliya**
- GitHub: [@Nandoliya-Shoeb](https://github.com/Nandoliya-Shoeb)
- Portfolio: Your Portfolio Link

## 🤝 Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Create an Issue on GitHub
- Contact: your-email@example.com

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Framework
- Open Source Community

---

**Last Updated:** April 2026
