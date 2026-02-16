# Contribution Platform

A Flask-based web application for crowdfunding contributions to community events like burials, weddings, medical emergencies, and more. Features secure admin authentication with multi-tenant data isolation, allowing each admin to independently manage their own fundraising campaigns. Integrated with M-Pesa STK Push for easy payment collection.

## Quick Start

1. **Create Admin Account**: Visit `/signup` to create a new admin account
2. **Login**: Use your credentials at `/login`
3. **Create Events**: Add new fundraising events from your admin dashboard
4. **Accept Contributions**: Receive contributions via M-Pesa STK Push
5. **Track Funds**: Monitor expenditures and fund usage by category

## Features

- **Event Management**: Create and manage fundraising events
- **Contribution Tracking**: Track all contributions in real-time
- **M-Pesa Integration**: STK Push payment integration for Kenyan market
- **Admin Authentication**: Secure signup/login system for admin accounts
- **Multi-Tenant Support**: Each admin account has isolated access to their own events and data
- **Admin Dashboard**: Complete admin interface for event and contribution management
- **Expenditure Tracking**: Monitor how funds are being spent with categorization
- **Progress Tracking**: Visual progress bars showing collection status
- **Dark Mode**: Optional dark theme with localStorage persistence
- **PostgreSQL/SQLite Database**: Robust data storage and retrieval
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Migrate
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: Werkzeug password hashing
- **Payments**: M-Pesa STK Push API
- **Server**: Gunicorn
- **Theme**: Forest green (#2d5016) with dark mode support

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Setup

1. **Clone the repository**
   ```bash
   cd /home/fiddawg/PycharmProjects/finance_manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb contribution_db
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your configuration:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/contribution_db
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=your_passkey
   MPESA_ENV=sandbox  # Use 'production' for live
   SECRET_KEY=your-secret-key
   ```

6. **Initialize database**
   ```bash
   flask db upgrade
   ```

7. **Run development server**
   ```bash
   python run.py
   ```

   Server will be available at `http://localhost:5000`

## Usage

### For Users

1. Navigate to the home page
2. Browse active fundraising events
3. Click "View Details" on an event
4. Click "Contribute Now" to make a contribution
5. Enter your details and contribution amount
6. STK Push will be sent to your phone - enter your M-Pesa PIN
7. Contribution will be recorded once payment is complete

### For Administrators

#### First Time Setup
1. Visit `http://localhost:5000`
2. Click "Admin Login" button
3. Click "Create one here" to create a new admin account
4. Fill in username (min 3 chars), email, and password (min 6 chars)
5. Account is created and you're automatically logged in

#### Managing Events
1. Access your admin dashboard at `/admin`
2. Click "+ New Event" to create a fundraising event
3. Fill in event details (title, description, target amount, type)
4. View all **your events** and their progress (multi-tenant: only your data)
5. Edit events to change status or details
6. Add expenditures to track fund usage by category
7. View detailed contribution reports for each event
8. Click "Logout" to end your session

#### Data Security
- Each admin account only sees and manages their own events
- Other admins' events remain completely hidden
- Contributions and expenditures are tied to specific events
- Admin sessions are secure and require login

## API Endpoints

### Public API

- `GET /api/events` - Get all active events
- `GET /api/event/<id>` - Get event details
- `GET /api/event/<id>/contributions` - Get contributions for an event
- `GET /api/event/<id>/expenditures` - Get expenditures for an event
- `GET /api/event/<id>/expenditure/summary` - Get expenditure summary (total raised, spent, remaining)
- `POST /api/contribution` - Submit a new contribution
- `POST /api/payment/callback` - M-Pesa payment callback (webhook)

### Authentication Routes

- `GET /signup` - Create new admin account
- `POST /signup` - Submit signup form
- `GET /login` - Admin login page
- `POST /login` - Submit login credentials
- `GET /logout` - Logout and clear session

### Admin Routes (Require Login)

- `GET /admin` - Admin dashboard (only your events)
- `GET /admin/create-event` - Create event form
- `POST /admin/create-event` - Create new event (linked to your account)
- `GET /admin/event/<id>/edit` - Edit event form (only if you own it)
- `POST /admin/event/<id>/edit` - Update event (only if you own it)
- `GET /admin/event/<id>` - Event details (admin view, only if you own it)
- `GET /admin/event/<id>/expenditure/add` - Add expenditure form
- `POST /admin/event/<id>/expenditure/add` - Create new expenditure
- `POST /admin/expenditure/<id>/delete` - Delete expenditure record (only if you own the event)

## Event Types

The platform supports the following event types:

- **Burial**: For funeral arrangements and related costs
- **Wedding**: For wedding celebrations and expenses
- **Community**: For community projects and initiatives
- **Medical**: For medical emergencies and treatment costs
- **Education**: For school fees and educational programs
- **Other**: For miscellaneous events

## M-Pesa Integration

### STK Push Flow

1. User enters phone number and amount
2. Application calls M-Pesa STK Push API
3. M-Pesa sends prompt to user's phone
4. User enters PIN to authorize payment
5. Payment is processed
6. M-Pesa sends callback notification
7. Contribution is marked as completed
8. Event progress is updated

### Setup M-Pesa Credentials

1. Register as M-Pesa API consumer at [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Generate Consumer Key and Secret
3. Get your Business Shortcode (Paybill/Till Number)
4. Generate M-Pesa Pass Key
5. Add credentials to `.env` file

## Database Models

### User
- username (unique, min 3 chars)
- email (unique)
- password_hash (encrypted with werkzeug)
- created_at
- Relationship: One-to-Many with Event

### Event
- admin_id (foreign key to User - multi-tenant)
- title, description, event_type
- organizer_name, organizer_phone
- target_amount, current_amount
- event_date, created_at, updated_at
- status (active/closed/completed)
- Relationships: One-to-Many with Contribution, One-to-Many with Expenditure

### Contribution
- event_id, contributor_name, contributor_phone
- amount, payment_method, transaction_id
- status (pending/completed/failed)

### Expenditure
- event_id, description, amount
- category (supplies, labor, transport, venue, catering, medicine, utilities, other)
- approved_by, created_at
- receipt_url (optional)

### PaymentCallback
- Raw M-Pesa callback data for audit trail

## Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `MPESA_*` - M-Pesa credentials
- `FLASK_ENV` - development or production
- `PORT` - Server port (default: 5000)

## Security Considerations

- **Authentication**: Admin accounts use Werkzeug secure password hashing
- **Multi-Tenant Isolation**: Each admin only sees their own events via admin_id foreign key
- **Session Management**: Session-based authentication with SECRET_KEY
- **Access Control**: All admin routes require login_required decorator
- **HTTPS**: Always use HTTPS in production
- **M-Pesa Credentials**: Keep credentials secure (use environment variables)
- **Input Validation**: All user input validated on backend
- **Strong SECRET_KEY**: Use strong SECRET_KEY in .env
- **Regular Audits**: Regular security audits recommended
- **Database**: Use PostgreSQL with proper user permissions in production

## Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env file
Ensure PostgreSQL service is running (or use SQLite for dev)
If migration errors occur, try: rm app.db && python run.py (SQLite dev only)
```

### Cannot Login - Invalid Credentials
```
Ensure you've created an admin account via signup
Check username and password are correct
Passwords are case-sensitive
```

### Cannot See My Events in Admin
```
Ensure you're logged in as the admin who created the event
Each admin only sees their own events (multi-tenant data isolation)
Check you have permission to view the event
```

### 404 Error When Accessing Admin Event
```
The event doesn't exist OR
You don't own the event (multi-tenant security check)
Verify you're logged in as the correct admin account
```

### M-Pesa STK Push Not Sending
```
Verify API credentials in .env
Check callback URL is reachable
Ensure M-Pesa environment is correct (sandbox vs production)
```

### Payment Callback Not Received
```
Configure firewall to allow incoming webhooks
Ensure callback URL is publicly accessible
Check M-Pesa callback settings
Verify SECRET_KEY matches in .env
```

### Session Expires
```
This is normal - login again with your credentials
Consider adding password reset feature in future
```

### Dark Mode Not Persisting
```
Ensure browser allows localStorage
Check browser's privacy settings
Clear browser cache and try again
```

## Future Enhancements

- Password reset via email
- Admin profile management
- Event approval workflow
- Email notifications for contributions
- SMS updates for contributors
- Multiple payment methods (Bank transfer, card, Airtel Money)
- Advanced analytics and reporting
- Export to PDF/Excel
- Receipt image uploads
- Budget alerts
- Team fundraising features
- Social sharing
- Mobile app
- Admin activity logs
- Event visibility settings (public/private)
- Campaign templates

## License

MIT License - Free to use and modify

## Support

For issues and questions:
1. Check troubleshooting section
2. Review Flask and Flask-SQLAlchemy documentation
3. Check M-Pesa API troubleshooting guide
4. Review authentication and multi-tenant setup

## Project Status

✅ Core Features: Complete
✅ Authentication & Authorization: Complete
✅ Multi-Tenant Support: Implemented
✅ Expenditure Tracking: Complete
✅ Dark Mode: Implemented
⏳ Advanced Features: In Progress

## Contributors

Created with ❤️ for African communities

---

**Note**: This is a development setup. For production deployment, ensure proper security measures, SSL certificates, and regular backups are implemented.
