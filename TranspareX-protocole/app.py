from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, Fund, Transaction, AuditLog
from auth_service import token_required, admin_required, register_user, authenticate_user, log_audit
from blockchain_service import blockchain_service
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@transparex.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@transparex.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Default admin user created: admin@transparex.com / admin123")
    
    return app

app = create_app()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    blockchain_status = "connected" if blockchain_service.is_connected() else "disconnected"
    return jsonify({
        "status": "healthy",
        "blockchain": blockchain_status,
        "timestamp": datetime.utcnow().isoformat()
    })

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        result = register_user(username, email, password)
        status_code = 201 if result["success"] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({"success": False, "message": "Email and password required"}), 400
        
        result = authenticate_user(email, password)
        status_code = 200 if result["success"] else 401
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Fund management routes
@app.route('/api/funds', methods=['GET'])
@token_required
def get_funds(current_user):
    """Get all funds"""
    try:
        funds = Fund.query.all()
        return jsonify({
            "success": True,
            "funds": [fund.to_dict() for fund in funds]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/funds', methods=['POST'])
@token_required
@admin_required
def create_fund(current_user):
    """Create a new fund"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        total_amount = data.get('total_amount')
        
        if not all([name, total_amount]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        fund = Fund(
            name=name,
            description=description,
            total_amount=total_amount,
            remaining_amount=total_amount,
            created_by=current_user.id
        )
        
        db.session.add(fund)
        db.session.commit()
        
        log_audit(
            current_user.id,
            "Fund Created",
            f"Created fund: {name} with amount {total_amount}",
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            "success": True,
            "message": "Fund created successfully",
            "fund": fund.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Transaction routes
@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    """Get user's transactions"""
    try:
        if current_user.role == 'admin':
            transactions = Transaction.query.all()
        else:
            transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            "success": True,
            "transactions": [tx.to_dict() for tx in transactions]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transaction(current_user):
    """Create a new transaction"""
    try:
        data = request.get_json()
        fund_id = data.get('fund_id')
        recipient_address = data.get('recipient_address')
        amount = data.get('amount')
        
        if not all([fund_id, recipient_address, amount]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        # Check if fund exists and has sufficient balance
        fund = Fund.query.get(fund_id)
        if not fund:
            return jsonify({"success": False, "message": "Fund not found"}), 404
        
        if fund.remaining_amount < amount:
            return jsonify({"success": False, "message": "Insufficient fund balance"}), 400
        
        # Create transaction
        transaction = Transaction(
            fund_id=fund_id,
            user_id=current_user.id,
            recipient_address=recipient_address,
            amount=amount,
            status='pending'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Release funds via blockchain
        blockchain_result = blockchain_service.release_funds(recipient_address, amount)
        
        if blockchain_result["success"]:
            transaction.status = 'completed'
            transaction.transaction_hash = blockchain_result["transaction_hash"]
            transaction.completed_at = datetime.utcnow()
            
            # Update fund remaining amount
            fund.remaining_amount -= amount
        else:
            transaction.status = 'failed'
        
        db.session.commit()
        
        log_audit(
            current_user.id,
            "Transaction Created",
            f"Transaction created: {amount} to {recipient_address}",
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            "success": True,
            "message": "Transaction processed",
            "transaction": transaction.to_dict(),
            "blockchain_result": blockchain_result
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Blockchain routes
@app.route('/api/blockchain/balance')
@token_required
def get_blockchain_balance(current_user):
    """Get blockchain contract balance"""
    try:
        balance = blockchain_service.get_contract_balance()
        return jsonify({
            "success": True,
            "balance": balance
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/blockchain/events')
@token_required
def get_blockchain_events(current_user):
    """Get blockchain events"""
    try:
        events = blockchain_service.get_fund_released_events()
        return jsonify({
            "success": True,
            "events": events
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/blockchain/transaction/<tx_hash>')
@token_required
def get_transaction_details(current_user, tx_hash):
    """Get transaction details from blockchain"""
    try:
        details = blockchain_service.get_transaction_details(tx_hash)
        if details:
            return jsonify({
                "success": True,
                "transaction": details
            })
        else:
            return jsonify({"success": False, "message": "Transaction not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Dashboard routes
@app.route('/api/dashboard/stats')
@token_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics"""
    try:
        total_funds = Fund.query.count()
        total_transactions = Transaction.query.count()
        completed_transactions = Transaction.query.filter_by(status='completed').count()
        total_amount_disbursed = db.session.query(db.func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
        
        stats = {
            "total_funds": total_funds,
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "total_amount_disbursed": total_amount_disbursed,
            "blockchain_balance": blockchain_service.get_contract_balance()
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Audit routes
@app.route('/api/audit/logs')
@token_required
@admin_required
def get_audit_logs(current_user):
    """Get audit logs (admin only)"""
    try:
        logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
        return jsonify({
            "success": True,
            "logs": [log.to_dict() for log in logs]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
