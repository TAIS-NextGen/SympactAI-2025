# PumpWatch Backend API

**Industrial Pump Monitoring System - Backend Services**

A robust Node.js/Express API server providing comprehensive pump monitoring, user management, chatbot integration for the PumpWatch platform.

##  Features

###  **Authentication & Authorization**
- JWT-based user authentication
- Role-based access control (Admin, Technician, Inspector)
- Secure password hashing with bcrypt
- Session management and refresh tokens

###  **Pump Management**
- Complete CRUD operations for pump systems
- Multi-company pump inventory
- Maintenance scheduling and tracking
- Real-time status monitoring


##  Tech Stack

- **Runtime:** Node.js 18+
- **Framework:** Express.js
- **Database:** MongoDB with Mongoose ODM
- **Authentication:** JWT (jsonwebtoken)
- **Security:** bcrypt, helmet, cors
- **Environment:** dotenv

##  Quick Start

### Prerequisites
- Node.js 18+
- MongoDB 6.0+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mariem-Kammoun0/SympactAI.git
   cd SympactAI
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
  
   Configure your `.env` file:
   ```env
   # Database
   MONGO_URI=your-mongo-db-uri
   # Authentication
   JWT_SECRET=your-super-secret-jwt-key
   ```

4. **Seed the database (optional)**
   ```bash
   npm run test/seed.js
   ```

6. **Start the server**
   ```bash
   # Development mode
   npm run dev
   
   # Production mode
   npm start
   ```

##  API Endpoints

### Authentication
```http
POST   /api/auth/register       # User registration with validation
POST   /api/auth/login          # User login
POST   /api/auth/logout         # User logout (requires auth)
```
### User Management
```http
GET    /api/user/profile        # Get current user profile (requires auth)
```

### Pump Management
```http
GET    /api/pumps               # Get all pumps (requires auth)
POST   /api/pumps/add           # Create new pump (admin only)
GET    /api/pumps/dashboard/:id # Get specific pump dashboard (requires auth)
GET    /api/pumps/dashboard     # Get general pump dashboard (requires auth)
```

### Company Management
```http
GET    /api/company/all         # Get all companies (public)
GET    /api/company/info        # Get company details (admin only)
PUT    /api/company/update      # Update company details (admin only)
GET    /api/company/users       # Get company users (admin only)
GET    /api/company/dashboard   # Get company dashboard (admin only)
```

### System
```http
GET    /api/health              # Health check
GET    /api/stats               # System statistics
```
---

**Built within Tunisian AI Society NextGen - SympactAI** 
