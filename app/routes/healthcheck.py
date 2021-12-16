from app import app

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return 'OK', 200
