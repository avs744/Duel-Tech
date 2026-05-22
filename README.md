# DuelTech Web Application

A web application for comparing tech products with user authentication and admin functionality.

## Deployment on Vercel

### Prerequisites
- Vercel account
- Vercel CLI installed (`npm install -g vercel`)

### Setting up Environment Variables for Email

When deploying to Vercel, you need to set up environment variables for the contact form email functionality:

1. Log in to your Vercel dashboard
2. Select your project
3. Go to "Settings" > "Environment Variables"
4. Add the following variables:
   - `EMAIL_USER`: Your Gmail address or app email (e.g., youremail@gmail.com)
   - `EMAIL_PASSWORD`: Your Gmail app password (NOT your regular Gmail password)
   
For Gmail, you need to create an "App Password":
1. Go to your Google Account > Security
2. Enable 2-Step Verification if not already enabled
3. Under "App passwords", create a new app password
4. Use this generated password as your `EMAIL_PASSWORD`

### Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   python app.py
   ```

### Deployment Steps

1. Login to Vercel:
   ```
   vercel login
   ```

2. Deploy to Vercel:
   ```
   vercel
   ```

3. For production deployment:
   ```
   vercel --prod
   ```

## Features

- User authentication (register/login)
- Admin panel for managing products
- Product comparison tool
- Search functionality
- Contact form with email notifications to rishipadwal78@gmail.com
- Responsive design

## Database

The application uses SQLite for development. For production on Vercel, consider switching to a cloud-based database service as Vercel has a read-only filesystem in production.

## Requirements

- Python 3.7+
- MySQL Server 5.7+ (port 3308)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd dueltech
```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Configure MySQL:
   - Ensure MySQL server is running on port 3308
   - Create a user with the credentials:
     - Username: `Hola Amigo`
     - Password: `Rishhi@4273`
   - The database `dueltech_db` will be created automatically when running the initialization script

4. Initialize the database:
```
python init_db.py
```

5. Run the application:
```
python app.py
```

6. Access the application at http://localhost:5000

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## Usage

1. Register as a regular user or log in as admin
2. Regular users can:
   - Browse products
   - Compare products
   - View product details

3. Admin users can:
   - Manage products (add, edit, delete)
   - Manage users
   - Create other admin users

## Project Structure

- `app.py` - Main application file
- `init_db.py` - Database initialization script
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
- `requirements.txt` - Python dependencies 
=======
# Duel-Tech-Final-
>>>>>>> fe40a937f4f7f49bca3f6f6c216bfccd0b8f6ee5
