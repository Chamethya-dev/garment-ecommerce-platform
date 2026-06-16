from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ All tables created successfully!")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("\n📋 Tables created:")
    for table in tables:
        print(f"  - {table}")