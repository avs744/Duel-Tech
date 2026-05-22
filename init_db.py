from app import db, User, generate_password_hash

def init_database():
    try:
        # Create all tables from app models
        db.create_all()
        print("Tables created successfully!")
        
        # Check if admin user exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # Create admin user
            hashed_password = generate_password_hash('admin123')
            admin_user = User(
                username='admin',
                email='admin@dueltech.com',
                password=hashed_password,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database() 