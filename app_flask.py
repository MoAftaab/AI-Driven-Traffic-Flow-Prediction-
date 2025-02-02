from flask import Flask, jsonify, request, render_template
import route_finding as router
import datetime
from TrafficData.TrafficFlowPredictor import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def parse_date(date_string):
    try:
        date, time = date_string.split()
        year, month, day = date.split('/')
        hour, minute = time.split(':')
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    except:
        return datetime.datetime.now()

@app.route('/')
def home():
    models = [model.value for model in TrafficFlowModelsEnum]
    return render_template('index.html', models=models)

@app.route('/routes', methods=['POST'])
def get_routes():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    src = data.get('source')
    dest = data.get('destination')
    date_string = data.get('datetime')
    model_type = data.get('model', TrafficFlowModelsEnum.LSTM.value)
    
    if not src or not dest:
        return jsonify({"error": "Please provide source and destination"}), 400
        
    date = parse_date(date_string) if date_string else datetime.datetime.now()
    
    try:
        routes = router.runRouter(src, dest, date, model_type)
        if request.is_json:
            return jsonify({"routes": routes})
        else:
            return render_template('routes.html', routes=routes)
    except Exception as e:
        error = str(e)
        if request.is_json:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error), 500

@app.route('/predict', methods=['POST'])
def predict_traffic():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    point = data.get('scats')
    date_string = data.get('datetime')
    model_type = data.get('model', TrafficFlowModelsEnum.LSTM.value)
    
    if not point:
        return jsonify({"error": "Please provide SCATS number"}), 400
        
    date = parse_date(date_string) if date_string else datetime.datetime.now()
    
    try:
        predictor = TrafficFlowPredictor()
        flow = predictor.predict_traffic_flow(point, date, 4, model_type)
        
        result = {
            "scats": point,
            "datetime": date.strftime('%Y/%m/%d %I:%M:%S'),
            "prediction": flow,
            "unit": "veh/hr"
        }
        
        if request.is_json:
            return jsonify(result)
        else:
            return render_template('prediction.html', result=result)
    except ValueError as ve:
        error = "Invalid SCATS number"
        if request.is_json:
            return jsonify({"error": error}), 400
        else:
            return render_template('error.html', error=error), 400
    except Exception as e:
        error = str(e)
        if request.is_json:
            return jsonify({"error": error}), 500
        else:
            return render_template('error.html', error=error), 500

@app.route('/models', methods=['GET'])
def get_models():
    models = [model.value for model in TrafficFlowModelsEnum]
    if request.headers.get('Accept') == 'application/json':
        return jsonify({"models": models})
    else:
        return render_template('models.html', models=models)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
