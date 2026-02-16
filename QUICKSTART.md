# Contribution Platform - Quick Start Guide

## Project Overview

This is a Flask-based fundraising platform with M-Pesa STK Push integration, designed for collecting contributions to community events (burials, weddings, medical, education, etc.).

## Folder Structure

```
finance_manager/
├── app/                          # Main application folder
│   ├── __init__.py             # Flask app initialization
│   ├── models.py               # Database models
│   ├── routes.py               # All route handlers
│   ├── payments.py             # M-Pesa STK Push handler
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── index.html          # Homepage with events list
│   │   ├── event_detail.html   # Event detail & contribution form
│   │   └── admin/              # Admin templates
│   │       ├── dashboard.html  # Admin dashboard
│   │       ├── create_event.html
│   │       ├── edit_event.html
│   │       └── event_detail.html
│   └── static/                 # Static files
│       ├── css/style.css       # All styling
│       └── js/main.js          # Frontend JavaScript
├── migrations/                  # Database migrations (Alembic)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
└── README.md                    # Full documentation
```

## Installation Steps

### Step 1: Install Dependencies

```bash
cd /home/fiddawg/PycharmProjects/finance_manager
pip install -r requirements.txt
```

**Packages installed:**
- Flask (web framework)
- SQLAlchemy (ORM)
- Flask-Migrate (database migrations)
- PostgreSQL driver (psycopg2)
- Requests (HTTP library for M-Pesa)
- python-dotenv (environment variables)

### Step 2: Setup PostgreSQL Database

```bash
# Create database
createdb contribution_db

# Connect to database
psql contribution_db
```

If using different credentials, update `DATABASE_URL` in next step.

### Step 3: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

**Required settings:**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/contribution_db

# M-Pesa (get from https://developer.safaricom.co.ke/)
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_m_pesa_passkey
MPESA_ENV=sandbox  # Change to 'production' for live

# Flask
SECRET_KEY=generate-a-random-secret-key
FLASK_ENV=development
```

### Step 4: Initialize Database

```bash
# Create tables
flask db upgrade

# Or manually create:
python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

### Step 5: Run the Application

```bash
python run.py
```

Application will run at: **http://localhost:5000**

## Key Features

### For Users
- Browse active fundraising events by type
- View event progress with visual indicators
- Contribute via M-Pesa STK Push (automatic prompt)
- See recent contributors
- No registration required

### For Administrators
- Create new events with different types
- Edit event details and status
- Track all contributions in real-time
- View detailed analytics
- Download reports (optional enhancement)

**Access admin at:** `http://localhost:5000/admin`

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/events` | List all active events |
| POST | `/api/contribution` | Submit new contribution |
| POST | `/api/payment/callback` | Webhook for M-Pesa |
| GET | `/admin` | Admin dashboard |
| POST | `/admin/create-event` | Create event |

## Database Schema

### Events Table
- Stores event information
- Tracks target and current amounts
- Maintains status (active/closed/completed)

### Contributions Table
- Records each contribution
- Links to events
- Tracks payment status

### PaymentCallbacks Table
- Stores M-Pesa response logs
- Used for audit trail and debugging

## M-Pesa Setup

### Sandbox Testing
1. Go to [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Create account and log in
3. Create new app
4. Copy Consumer Key and Secret
5. Add credentials to `.env`
6. Use `MPESA_ENV=sandbox`

### Production
1. Complete M-Pesa business registration
2. Get real credentials
3. Change `MPESA_ENV=production`
4. Update callback URL to public domain

### Test Credentials for Sandbox
```
Phone: 254712345678
Amount: Any amount (will be simulated)
```

## Common Issues & Solutions

### 1. Database Connection Error
```
Error: could not connect to server
Solution: Ensure PostgreSQL is running
  - Linux: sudo service postgresql start
  - macOS: brew services start postgresql
```

### 2. M-Pesa STK Push Not Working
```
Error: Failed to get access token
Solution: 
  - Check credentials in .env
  - Verify firewall allows outbound HTTPS
  - Check if using correct environment (sandbox vs production)
```

### 3. Module Not Found Error
```
Solution: pip install -r requirements.txt
```

### 4. Port Already in Use
```
Solution: Change port in run.py or use:
  python run.py --port 5001
```

## Development Tips

### Create New Event (via admin)
1. Go to http://localhost:5000/admin
2. Click "+ New Event"
3. Fill in details
4. Save

### Test Contribution
1. Go to event detail page
2. Click "Contribute Now"
3. Enter test phone: 254712345678
4. Set amount (any amount in sandbox)
5. Click "Send STK Push"

### View Database
```bash
psql contribution_db
# List tables: \dt
# View data: SELECT * FROM events;
```

### Debug Mode
```python
# In run.py, set:
app.run(debug=True)
```

## Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker
```bash
docker build -t contribution-platform .
docker run -p 5000:5000 contribution-platform
```

### Using Heroku
```bash
heroku create your-app-name
git push heroku main
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Setup PostgreSQL
3. ✅ Configure `.env`
4. ✅ Run `python run.py`
5. 📝 Create first event in admin
6. 🧪 Test contribution flow
7. 🚀 Deploy to production

## Support Files

- **README.md** - Full documentation
- **.env.example** - Environment variables template
- **requirements.txt** - All dependencies listed

## Contributing

To add features:
1. Create new route in `app/routes.py`
2. Add database model if needed in `app/models.py`
3. Create template in `app/templates/`
4. Test thoroughly before deploying

---

**Ready to start?** Run: `python run.py`

Visit: http://localhost:5000
