# Expenditure Feature Guide

## Overview

The expenditure tracking feature allows administrators to record and monitor how funds are being spent for each event. This helps provide transparency to contributors about fund usage.

## Features

### 1. **Add Expenditure (Admin)**
- Record spending with description and category
- Support for 8 expense categories:
  - Supplies
  - Labor
  - Transport
  - Venue
  - Catering
  - Medicine
  - Utilities
  - Other

### 2. **Track Spending**
- View total expenditure vs. contributions
- See remaining balance available
- Calculate percentage of budget used
- Track by category

### 3. **Admin Dashboard**
Located at: **http://localhost:5000/admin/event/{event_id}**

**Expenditure Section:**
- Add new expenditure
- View all recorded expenses
- See expenditure summary (total spent, remaining balance, % of budget)
- Delete expenditure records
- Approve/track spending by authorized person

### 4. **Public Transparency**
On the event detail page, visitors can see:
- How much has been raised
- How much has been spent
- Remaining balance
- Breakdown by spending category

## How to Use

### Adding an Expenditure

1. Go to Admin Dashboard: **http://localhost:5000/admin**
2. Click on an event to view details
3. Click **"+ Add Expenditure"** button
4. Fill in the form:
   - **Description**: What was spent on (e.g., "Rental supplies", "Medical expenses")
   - **Amount**: Cost in KES
   - **Category**: Select the spending category
   - **Approved By**: Name of person authorizing this expense
5. Click **"Add Expenditure"**

### Viewing Expenditures

**Admin View:**
- Event detail page shows:
  - Summary box with total raised, spent, and remaining
  - Table of all expenditures with dates
  - Option to delete records

**Public View:**
- Event detail page shows:
  - Progress bars for contributions and spending
  - Breakdown by spending category
  - Transparency on how funds are used

### Database Tables

**Expenditure Table:**
- `id`: Unique identifier
- `event_id`: Link to event
- `description`: What was purchased/spent on
- `amount`: Cost in KES
- `category`: Expense category
- `approved_by`: Name of approver
- `receipt_url`: Optional link to receipt
- `created_at`: When recorded
- `updated_at`: Last modification

## API Endpoints

### Get All Expenditures for Event
```
GET /api/event/{event_id}/expenditures
```
Returns list of all expenditure records.

### Get Expenditure Summary
```
GET /api/event/{event_id}/expenditure/summary
```
Returns:
- `total_raised`: Total contributions
- `total_expenditure`: Total spent
- `remaining`: Balance available
- `by_category`: Breakdown by category
- `count`: Number of records

## Key Information

- **Currency**: All amounts in KES (Kenya Shilling)
- **Categories**: Pre-defined for consistency
- **Approval Tracking**: Records who approved each expense
- **Transparency**: Public can see how funds are used
- **No Deletion Prevention**: Admin can delete records (implement soft delete in production)

## Example Workflow

```
Event: "Community School Building"
Target: KES 500,000
Raised: KES 450,000

Expenditures:
├── Venue Rental: KES 50,000
├── Building Materials: KES 200,000
├── Labor: KES 150,000
├── Transport: KES 30,000
└── Catering: KES 20,000

Total Spent: KES 450,000
Remaining: KES 0
Percentage Used: 100%
```

## Best Practices

1. **Record Promptly**: Add expenditure records soon after spending
2. **Get Approval**: Ensure spending is approved before recording
3. **Keep Receipts**: Store physical receipts for audits
4. **Description Details**: Be specific about what was purchased
5. **Correct Category**: Choose appropriate category for better tracking
6. **Regular Reviews**: Check expenditure reports weekly

## Future Enhancements

- Upload receipt images
- Expenditure approval workflow
- Budget alerts (warn if exceeding)
- Export reports to PDF/Excel
- Receipt photo gallery
- Audit trail with edit history
- Task assignment for spending
- Budget forecasting

## Support

For issues or questions about expenditure tracking, check the main README.md or contact the admin panel.
