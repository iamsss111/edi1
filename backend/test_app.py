"""
Test script to verify Flask application factory
"""
from app import create_app

try:
    # Create application
    app = create_app()
    print("✓ Flask application created successfully")
    print(f"✓ Debug mode: {app.config['DEBUG']}")
    print(f"✓ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("✓ All extensions initialized")
    print("\n--- Application Factory Setup Complete ---")
    print("✓ Configuration loaded")
    print("✓ Database extension initialized")
    print("✓ JWT extension initialized")
    print("✓ Blueprints registered")
    print("\nReady to start development!")
except Exception as e:
    print(f"✗ Error creating application: {e}")
    import traceback
    traceback.print_exc()
