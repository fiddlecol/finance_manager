from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app import db
from app.models import Event, Contribution, EventType, PaymentCallback, Expenditure, ExpenditureCategory, User
from app.payments import stk_handler
from datetime import datetime
import json
from functools import wraps

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__)

# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================
def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# AUTH ROUTES
# ============================================================================
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['admin_id'] = user.id
            session['admin_username'] = user.username
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Logout Admin"""
    session.clear()
    return redirect(url_for('main.index'))

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Admin signup page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        email = request.form.get('email')
        
        # Validation
        if not username or not password or not email:
            return render_template('signup.html', error='All fields are required')
        
        if len(username) < 3:
            return render_template('signup.html', error='Username must be at least 3 characters')
        
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters')
        
        if password != password_confirm:
            return render_template('signup.html', error='Passwords do not match')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', error='Username already exists')
        
        # Check if email exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('signup.html', error='Email already registered')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login the user
        session['admin_id'] = user.id
        session['admin_username'] = user.username
        
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('signup.html')



# MAIN ROUTES (Public)
# ============================================================================

@main_bp.route('/')
def index():
    """Homepage with list of active events"""
    events = Event.query.filter_by(status='active').all()
    return render_template('index.html', events=events)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    """Event detail page"""
    event = Event.query.get_or_404(event_id)
    contributors = Contribution.query.filter_by(
        event_id=event_id,
        status='completed'
    ).order_by(Contribution.created_at.desc()).all()
    return render_template('event_detail.html', event=event, contributors=contributors)

@main_bp.route('/contribute/<int:event_id>', methods=['GET', 'POST'])
def contribute(event_id):
    """Contribution form page"""
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        return redirect(url_for('api.process_contribution', event_id=event_id))
    return render_template('contribute.html', event=event)

# ============================================================================
# API ROUTES
# ============================================================================

@api_bp.route('/events', methods=['GET'])
def get_events():
    """Get all active events"""
    events = Event.query.filter_by(status='active').all()
    return jsonify([event.to_dict() for event in events])

@api_bp.route('/event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get event details"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())

@api_bp.route('/event/<int:event_id>/contributions', methods=['GET'])
def get_event_contributions(event_id):
    """Get contributions for an event"""
    contributions = Contribution.query.filter_by(
        event_id=event_id,
        status='completed'
    ).all()
    return jsonify([contrib.to_dict() for contrib in contributions])

@api_bp.route('/contribution', methods=['POST'])
def process_contribution():
    """Process a new contribution with STK Push"""
    data = request.get_json() or request.form
    
    try:
        event_id = int(data.get('event_id'))
        amount = float(data.get('amount'))
        phone = data.get('phone')
        name = data.get('name', 'Anonymous')
        
        if not all([event_id, amount, phone]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if amount < 1:
            return jsonify({'error': 'Minimum contribution is KES 1'}), 400
        
        # Verify event exists
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Create contribution record
        contribution = Contribution(
            event_id=event_id,
            contributor_name=name,
            contributor_phone=phone,
            amount=amount,
            payment_method='mpesa',
            status='pending'
        )
        db.session.add(contribution)
        db.session.commit()
        
        # Initiate STK Push - FIXED
        response = stk_handler.initiate_stk_push(
            phone_number=phone,
            amount=int(amount),
            contribution_id=contribution.id,  # <-- use contribution_id
            description=f"Contribution to {event.title}"
        )
        
        if 'error' in response:
            contribution.status = 'failed'
            db.session.commit()
            return jsonify({'error': response['error']}), 400
        
        return jsonify({
            'success': True,
            'message': 'STK Push sent successfully',
            'checkout_request_id': response.get('CheckoutRequestID'),
            'contribution_id': contribution.id
        })
    
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/payment/callback', methods=['POST'])
def payment_callback():
    """M-Pesa payment callback"""
    try:
        callback_data = request.get_json()
        
        # Store raw callback
        payment_callback = PaymentCallback(
            raw_response=callback_data
        )
        
        # Parse callback
        result = callback_data.get('Body', {}).get('stkCallback', {})
        result_code = result.get('ResultCode', -1)
        
        if result_code == 0:
            # Payment successful
            metadata = result.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract details from metadata
            payment_data = {}
            for item in metadata:
                name = item.get('Name')
                value = item.get('Value')
                if name == 'Amount':
                    payment_data['amount'] = value
                elif name == 'MpesaReceiptNumber':
                    payment_data['receipt'] = value
                elif name == 'TransactionDate':
                    payment_data['date'] = value
                elif name == 'PhoneNumber':
                    payment_data['phone'] = value
            
            # Update payment callback record
            payment_callback.mpesa_receipt_number = payment_data.get('receipt')
            payment_callback.phone_number = payment_data.get('phone')
            payment_callback.amount = payment_data.get('amount')
            payment_callback.status = 'success'
            
            # Extract contribution ID from CheckoutRequestID or AccountReference
            account_ref = result.get('CheckoutRequestID')
            
            # Update contribution if found
            if account_ref:
                contribution = Contribution.query.filter(
                    (Contribution.id.cast(db.String) == account_ref.split('-')[-1])
                ).first()
                
                if contribution:
                    contribution.status = 'completed'
                    contribution.transaction_id = payment_data.get('receipt')
                    
                    # Update event's current amount
                    contribution.event.current_amount += contribution.amount
                    
                    payment_callback.contribution_id = contribution.id
                    db.session.commit()
                    
                    return jsonify({'status': 'success','message': 'Payment processed'}), 200
        
        else:
            # Payment failed
            payment_callback.status = 'failed'
        
        db.session.add(payment_callback)
        db.session.commit()
        
        return jsonify({'status': 'ok'}), 200
    
    except Exception as e:
        print(f"Callback error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/event/<int:event_id>/expenditures', methods=['GET'])
def get_event_expenditures(event_id):
    """Get all expenditures for an event"""
    expenditures = Expenditure.query.filter_by(event_id=event_id).order_by(Expenditure.created_at.desc()).all()
    return jsonify([exp.to_dict() for exp in expenditures])

@api_bp.route('/event/<int:event_id>/expenditure/summary', methods=['GET'])
def get_expenditure_summary(event_id):
    """Get expenditure summary for an event"""
    event = Event.query.get_or_404(event_id)
    expenditures = Expenditure.query.filter_by(event_id=event_id).all()
    
    total_expenditure = sum(exp.amount for exp in expenditures)
    remaining = event.current_amount - total_expenditure
    
    # Group by category
    by_category = {}
    for exp in expenditures:
        cat = exp.category.value
        if cat not in by_category:
            by_category[cat] = 0
        by_category[cat] += exp.amount
    
    return jsonify({
        'total_raised': event.current_amount,
        'total_expenditure': total_expenditure,
        'remaining': remaining,
        'by_category': by_category,
        'count': len(expenditures)
    })

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@admin_bp.route('/')
@login_required
def admin_dashboard():
    """Admin dashboard - shows only this admin's events"""
    admin_id = session.get('admin_id')
    events = Event.query.filter_by(admin_id=admin_id).all()
    total_contributions = db.session.query(db.func.coalesce(db.func.sum(Contribution.amount), 0)).filter(
        Contribution.status == 'completed',
        Contribution.event_id.in_([e.id for e in events])
    ).scalar()
    total_events = len(events)
    
    return render_template('admin/dashboard.html', 
                          events=events,
                          total_contributions=total_contributions,
                          total_events=total_events)

@admin_bp.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new fundraising event"""
    if request.method == 'POST':
        try:
            admin_id = session.get('admin_id')
            event = Event(
                admin_id=admin_id,
                title=request.form.get('title'),
                description=request.form.get('description'),
                event_type=EventType[request.form.get('event_type', 'COMMUNITY').upper()],
                organizer_name=request.form.get('organizer_name'),
                organizer_phone=request.form.get('organizer_phone'),
                target_amount=float(request.form.get('target_amount')),
                event_date=datetime.fromisoformat(request.form.get('event_date')) if request.form.get('event_date') else None
            )
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            return render_template('admin/create_event.html', error=str(e))
    
    return render_template('admin/create_event.html', event_types=[et.value for et in EventType])

@admin_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edit event - only if owner"""
    admin_id = session.get('admin_id')
    event = Event.query.filter_by(id=event_id, admin_id=admin_id).first_or_404()
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.target_amount = float(request.form.get('target_amount'))
        event.status = request.form.get('status')
        db.session.commit()
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/edit_event.html', event=event, event_types=[et.value for et in EventType])

@admin_bp.route('/event/<int:event_id>', methods=['GET'])
@login_required
def event_admin_detail(event_id):
    """View event details in admin - only if owner"""
    admin_id = session.get('admin_id')
    event = Event.query.filter_by(id=event_id, admin_id=admin_id).first_or_404()
    contributions = Contribution.query.filter_by(event_id=event_id).all()
    expenditures = Expenditure.query.filter_by(event_id=event_id).order_by(Expenditure.created_at.desc()).all()
    
    # Calculate totals
    total_expenditure = sum(exp.amount for exp in expenditures)
    remaining = event.current_amount - total_expenditure
    
    return render_template('admin/event_detail.html', 
                          event=event, 
                          contributions=contributions,
                          expenditures=expenditures,
                          total_expenditure=total_expenditure,
                          remaining=remaining)

@admin_bp.route('/event/<int:event_id>/expenditure/add', methods=['GET', 'POST'])
@login_required
def add_expenditure(event_id):
    """Add new expenditure for an event - only if owner"""
    admin_id = session.get('admin_id')
    event = Event.query.filter_by(id=event_id, admin_id=admin_id).first_or_404()
    
    if request.method == 'POST':
        try:
            expenditure = Expenditure(
                event_id=event_id,
                description=request.form.get('description'),
                amount=float(request.form.get('amount')),
                category=ExpenditureCategory[request.form.get('category', 'OTHER').upper()],
                approved_by=request.form.get('approved_by')
            )
            db.session.add(expenditure)
            db.session.commit()
            return redirect(url_for('admin.event_admin_detail', event_id=event_id))
        except Exception as e:
            return render_template('admin/add_expenditure.html', 
                                 event=event, 
                                 error=str(e),
                                 categories=[cat.value for cat in ExpenditureCategory])
    
    return render_template('admin/add_expenditure.html', 
                          event=event,
                          categories=[cat.value for cat in ExpenditureCategory])

@admin_bp.route('/expenditure/<int:expenditure_id>/delete', methods=['POST'])
@login_required
def delete_expenditure(expenditure_id):
    """Delete an expenditure record - only if owner of event"""
    admin_id = session.get('admin_id')
    expenditure = Expenditure.query.get_or_404(expenditure_id)
    
    # Check if admin owns the event
    event = Event.query.filter_by(id=expenditure.event_id, admin_id=admin_id).first_or_404()
    
    event_id = expenditure.event_id
    db.session.delete(expenditure)
    db.session.commit()
    return redirect(url_for('admin.event_admin_detail', event_id=event_id))
