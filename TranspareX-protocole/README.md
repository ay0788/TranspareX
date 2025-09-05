# TranspareX - AI & Blockchain for Financial Transparency

![TranspareX Logo](https://raw.githubusercontent.com/ay0788/TranspareX/main/tx.jpg)

## Overview

TranspareX is a comprehensive platform that leverages AI and blockchain technology to enhance transparency, accountability, and efficiency in public sector financial management. The platform provides real-time monitoring, secure transactions, and intelligent analytics for fund management.

## Features

### 🔐 Authentication & Authorization
- User registration and login system
- Role-based access control (Admin, User, Auditor)
- JWT-based authentication
- Audit logging for all user actions

### 💰 Fund Management
- Create and manage multiple funds
- Real-time fund balance tracking
- Fund status monitoring (Active, Suspended, Closed)
- Detailed fund analytics

### 🔗 Blockchain Integration
- Ethereum smart contract integration
- Secure fund disbursements
- Immutable transaction records
- Real-time blockchain event monitoring
- Transaction hash verification

### 📊 Dashboard & Analytics
- Real-time dashboard with key metrics
- Transaction history and status tracking
- Blockchain event monitoring
- Fund performance analytics
- User activity logs

### 🛡️ Security Features
- End-to-end encryption
- Secure API endpoints
- Input validation and sanitization
- CORS protection
- SQL injection prevention

## Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Web3.py** - Ethereum blockchain integration
- **JWT** - Authentication tokens
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **Vanilla JavaScript** - Interactive user interface
- **Font Awesome** - Icons and visual elements
- **CSS Grid/Flexbox** - Responsive layout

### Database
- **SQLite** (Development) - Lightweight local database
- **PostgreSQL** (Production) - Robust production database

### Blockchain
- **Ethereum** - Smart contract platform
- **Ganache** - Local blockchain development
- **Web3.js** - Blockchain interaction

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js (for blockchain development)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/TranspareX.git
cd TranspareX/TranspareX-protocole
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Database Configuration
DATABASE_URL=sqlite:///transparex.db

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Blockchain Configuration
GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x9b64DE133BAb117b4F37cf7fE239BF5e4C062aeD

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### 4. Initialize the Database
The database will be automatically created when you first run the application.

### 5. Start the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Default Credentials

- **Admin Account**: admin@transparex.com / admin123
- **Role**: Administrator with full access

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/health` - Health check

### Fund Management
- `GET /api/funds` - Get all funds
- `POST /api/funds` - Create new fund (Admin only)

### Transaction Management
- `GET /api/transactions` - Get user transactions
- `POST /api/transactions` - Create new transaction

### Blockchain Integration
- `GET /api/blockchain/balance` - Get contract balance
- `GET /api/blockchain/events` - Get blockchain events
- `GET /api/blockchain/transaction/<hash>` - Get transaction details

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Audit
- `GET /api/audit/logs` - Get audit logs (Admin only)

## Smart Contract

The platform uses a Solidity smart contract (`FundDisbursement.sol`) for secure fund management:

### Key Functions
- `deposit()` - Deposit funds to the contract
- `releaseFunds(address, uint256)` - Release funds to recipient
- `getContractBalance()` - Get total contract balance
- `getBalance(address)` - Get account balance

### Events
- `FundsDeposited` - Emitted when funds are deposited
- `FundReleased` - Emitted when funds are released

## Usage Guide

### 1. User Registration
- Click "Register" to create a new account
- Fill in username, email, and password
- Login with your credentials

### 2. Fund Management (Admin)
- Login as admin to create funds
- Set fund name, description, and total amount
- Monitor fund status and remaining balance

### 3. Transaction Creation
- Select a fund with available balance
- Enter recipient Ethereum address
- Specify transaction amount
- Submit transaction for blockchain processing

### 4. Dashboard Monitoring
- View real-time statistics
- Monitor transaction status
- Track blockchain events
- Review audit logs

## Development

### Project Structure
```
TranspareX-protocole/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── auth_service.py       # Authentication services
├── blockchain_service.py # Blockchain integration
├── run.py               # Application startup script
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   └── index.html
├── static/              # Static assets
│   ├── style.css
│   └── app.js
└── FundDisbursement.sol # Smart contract
```

### Adding New Features
1. Create new models in `models.py`
2. Add API endpoints in `app.py`
3. Update frontend in `static/app.js`
4. Add corresponding UI elements in `templates/index.html`

### Database Migrations
The application uses SQLAlchemy with automatic table creation. For production, consider using Flask-Migrate for proper database versioning.

## Security Considerations

### Production Deployment
- Change default secret keys
- Use environment variables for sensitive data
- Enable HTTPS
- Configure proper CORS settings
- Use a production database (PostgreSQL)
- Implement rate limiting
- Add input validation and sanitization

### Smart Contract Security
- Audit smart contracts before deployment
- Use established patterns and libraries
- Implement proper access controls
- Test thoroughly on testnets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team

## Acknowledgments

- **Aya SDOUR**: [LinkedIn](https://www.linkedin.com/in/aya-s-689519327)
- **Moavia Hassan**: [LinkedIn](https://www.linkedin.com/in/moaviahassan)
- **Muhammad Ilyas**: [LinkedIn](https://www.linkedin.com/in/muhammad-ilyas-ibrahim)

---

**TranspareX** - Revolutionizing Financial Transparency with AI and Blockchain Technology
