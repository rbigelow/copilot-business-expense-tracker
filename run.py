from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Use environment variable to control debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
