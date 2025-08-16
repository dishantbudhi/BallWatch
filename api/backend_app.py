"""Backend app runner - create and run the Flask app."""

from backend.rest_entry import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
