# Contribution Platform

A Flask-based web application for crowdfunding contributions to community events like burials, weddings, medical emergencies, and more. Integrated with M-Pesa STK Push for easy payment collection.

## Features

- **Event Management**: Create and manage fundraising events
- **Contribution Tracking**: Track all contributions in real-time
- **M-Pesa Integration**: STK Push payment integration for Kenyan market
- **Admin Dashboard**: Complete admin interface for event and contribution management
- **Expenditure Tracking**: Monitor how funds are being spent
- **Progress Tracking**: Visual progress bars showing collection status
- **PostgreSQL/SQLite Database**: Robust data storage and retrieval
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Migrate
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Payments**: M-Pesa STK Push API
- **Server**: Gunicorn

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

1. Navigate to `/admin` to access the admin dashboard
2. Click "New Event" to create a fundraising event
3. Fill in event details (title, description, target amount, type)
4. View all events and their progress
5. Edit events to change status or details
6. View detailed contribution reports

## API Endpoints

### Public API

- `GET /api/events` - Get all active events
- `GET /api/event/<id>` - Get event details
- `GET /api/event/<id>/contributions` - Get contributions for an event
- `GET /api/event/<id>/expenditures` - Get expenditures for an event
- `GET /api/event/<id>/expenditure/summary` - Get expenditure summary (total raised, spent, remaining)
- `POST /api/contribution` - Submit a new contribution
- `POST /api/payment/callback` - M-Pesa payment callback (webhook)

### Admin Routes

- `GET /admin` - Admin dashboard
- `GET /admin/create-event` - Create event form
- `POST /admin/create-event` - Create new event
- `GET /admin/event/<id>/edit` - Edit event form
- `POST /admin/event/<id>/edit` - Update event
- `GET /admin/event/<id>` - Event details (admin view)
- `GET /admin/event/<id>/expenditure/add` - Add expenditure form
- `POST /admin/event/<id>/expenditure/add` - Create new expenditure
- `POST /admin/expenditure/<id>/delete` - Delete expenditure record

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

### Event
- title, description, event_type
- organizer_name, organizer_phone
- target_amount, current_amount
- event_date, created_at, updated_at
- status (active/closed/completed)

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

- Always use HTTPS in production
- Keep M-Pesa credentials secure (use environment variables)
- Validate all user input
- Use strong SECRET_KEY
- Enable CORS only for trusted domains
- Regular security audits recommended

## Troubleshooting

### Database Connection Error
```
Check DATABASE_URL in .env file
Ensure PostgreSQL service is running
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
```

## Future Enhancements

- Email notifications
- SMS updates
- Multiple payment methods (Bank transfer, card)
- Analytics and reporting
- Mobile app
- Team fundraising features
- Social sharing

## License

MIT License - Free to use and modify

## Support

For issues and questions:
1. Check troubleshooting section
2. Review FastAPI/Flask documentation
3. Check M-Pesa API troubleshooting guide

## Contributors

Created with ❤️ for African communities

---

**Note**: This is a development setup. For production deployment, ensure proper security measures, SSL certificates, and regular backups are implemented.
