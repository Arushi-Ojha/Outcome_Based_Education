# Outcome Based Education (OBE) Tracking System

A robust backend tracking system for outcome-based education mapping, attainment calculation, and institutional hierarchy management.

> ⚠️ **Prerequisites Warning**
> Before you begin, ensure that you have **Python 3.10+** installed on your machine and accessible via your terminal. You should also have a code editor or IDE (like VS Code) ready to run this project.

## 🚀 Getting Started

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/Arushi-Ojha/Outcome_Based_Education.git
cd Outcome_Based_Education
```

### 2. Set up the Environment
It is highly recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Navigate into the `backend` folder and install the required Python packages:
```bash
cd backend
pip install -r requirements.txt
```

### 4. Database Setup
The system uses TiDB (MySQL compatible). You need to set up your `.env` file in the `backend/` directory with the following variables:
```env
DB_HOST=your_tidb_host
DB_PORT=4000
DB_USER=your_tidb_user
DB_PASSWORD=your_tidb_password
DB_NAME=your_database_name

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

### 5. Run the Server
Because the core application files are safely isolated in the `main/` directory, you must run the server from the root `backend/` directory using this exact command:

```bash
uvicorn main.main:app --reload
```

The API will now be running locally. You can access the Interactive Swagger API Documentation at:
**http://127.0.0.1:8000/docs**

---

## 📁 Directory Structure
- `backend/main/` - Core application (Models, Routes, Schemas, CRUD logic)
- `backend/fixes/` - Standalone database migration and fix scripts
- `backend/documentation/` - Generated API docs and Excel references
