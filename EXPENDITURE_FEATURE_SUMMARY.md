# ✨ Expenditure Tracking Feature - Implementation Summary

## What Was Added

Your Contribution Platform now includes a complete **Expenditure Tracking System** to monitor how funds are being spent for each event.

## New Components

### 1. **Database Model** (`app/models.py`)
- `Expenditure` table with fields:
  - Description of spending
  - Amount spent (in KES)
  - Category (Supplies, Labor, Transport, Venue, Catering, Medicine, Utilities, Other)
  - Approved by (person authorizing)
  - Receipt URL (optional)
  - Timestamps

### 2. **API Routes** (`app/routes.py`)
- `GET /api/event/<id>/expenditures` - List all expenditures
- `GET /api/event/<id>/expenditure/summary` - Get spending summary
- `GET /admin/event/<id>/expenditure/add` - Add expenditure form
- `POST /admin/event/<id>/expenditure/add` - Create expenditure
- `POST /admin/expenditure/<id>/delete` - Delete expenditure

### 3. **Admin Templates**
- `admin/add_expenditure.html` - Form to record spending
- Updated `admin/event_detail.html` - Shows expenditure table and summary

### 4. **Public Transparency**
- Event detail page displays:
  - Total amount raised
  - Total amount spent
  - Remaining balance
  - Spending breakdown by category

### 5. **JavaScript Features** (`app/static/js/main.js`)
- `loadExpenditureSummary()` - Fetches and displays spending data
- Automatic formatting of currencies
- Real-time calculation of remaining balance

### 6. **Styling** (`app/static/css/style.css`)
- Color-coded expenditure categories
- Responsive expenditure tables
- Summary cards with spending data

## How to Use

### Admin: Add Spending Record
1. Go to Admin Dashboard: `http://localhost:5000/admin`
2. Click on an event
3. Scroll to "Expenditures" section
4. Click **"+ Add Expenditure"**
5. Fill in:
   - Description (what was purchased)
   - Amount in KES
   - Category
   - Approved by (your name)
6. Submit

### Admin: View Spending Report
In event detail (admin view), you'll see:
- **Summary card** showing:
  - Total Raised: KES X
  - Total Expenditure: KES Y
  - Remaining Balance: KES Z
  - Expenditure %: XX%
- **Table** with all spending records
- **Delete button** to remove incorrect entries

### Public: See Fund Usage
On the event detail page (public), visitors see:
- How much money was raised
- How much has been spent
- How much remains
- Breakdown by spending category (pie chart data)

## Database Schema

```sql
CREATE TABLE expenditures (
    id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,
    description VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    approved_by VARCHAR(100),
    receipt_url VARCHAR(500),
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
```

## Expenditure Categories

| Category | Use For |
|----------|---------|
| **Supplies** | Materials, equipment, supplies |
| **Labor** | Wages, consultant fees |
| **Transport** | Fuel, vehicle rental, logistics |
| **Venue** | Hall rental, location costs |
| **Catering** | Food, beverages |
| **Medicine** | Medical supplies, treatment |
| **Utilities** | Electricity, water, communications |
| **Other** | Miscellaneous expenses |

## Features

✅ Add unlimited expenditure records
✅ Categorize spending
✅ Track who approved each expense
✅ Calculate remaining balance automatically
✅ Show spending breakdown to public
✅ Delete incorrect entries
✅ Real-time balance updates
✅ Responsive design

## Example Usage

```
Event: Community Healthcare Drive
Target: KES 200,000
Raised: KES 180,000

Expenditures:
- Medical Supplies: KES 80,000
- Labor (Doctors): KES 60,000
- Transport: KES 20,000
- Catering: KES 15,000
- Total Spent: KES 175,000
- Remaining: KES 5,000
- Budget Used: 97.2%
```

## API Usage Examples

### Get all expenditures
```bash
curl http://localhost:5000/api/event/1/expenditures
```

### Get spending summary
```bash
curl http://localhost:5000/api/event/1/expenditure/summary
```

Response:
```json
{
    "total_raised": 180000,
    "total_expenditure": 175000,
    "remaining": 5000,
    "by_category": {
        "medicine": 80000,
        "labor": 60000,
        "transport": 20000,
        "catering": 15000
    },
    "count": 4
}
```

## Files Modified

1. `app/models.py` - Added Expenditure model
2. `app/routes.py` - Added expenditure routes
3. `app/templates/admin/event_detail.html` - Added expenditure UI
4. `app/templates/event_detail.html` - Added "How funds are used"
5. `app/static/css/style.css` - Added expenditure styling
6. `app/static/js/main.js` - Added expenditure loading function
7. `README.md` - Updated with expenditure info
8. Created `app/templates/admin/add_expenditure.html` - New template
9. Created `EXPENDITURE_GUIDE.md` - Feature guide

## What's Next?

Future enhancements could include:
1. Receipt image upload functionality
2. Expenditure approval workflow
3. Budget alerts (warn if exceeding target)
4. PDF/Excel reports
5. Edit expenditure records
6. Detailed audit logs
7. Monthly spending trends
8. Task assignment for spending

## Testing

1. Create a new event with target amount
2. Add some test contributions
3. Add multiple expenditure records with different categories
4. View admin page to see spending breakdown
5. View public event page to see transparency
6. Test API endpoints with curl or Postman

## Technical Notes

- Uses SQLite for development (can switch to PostgreSQL)
- Expenditure amounts stored as Float
- Categories use Python Enum for type safety
- Supports soft deletes (can be enhanced)
- All currency in KES
- Timestamps in UTC

---

**Your expenditure tracking system is ready!** 🎉

Access it at: `http://localhost:5000/admin`

See the detailed guide: [EXPENDITURE_GUIDE.md](EXPENDITURE_GUIDE.md)
