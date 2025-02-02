from flask import Flask, jsonify, request
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

@app.route('/routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    
    src = data.get('source')
    dest = data.get('destination')
    date_string = data.get('datetime')
    model_type = data.get('model', TrafficFlowModelsEnum.LSTM.value)
    
    if not src or not dest:
        return jsonify({"error": "Please provide source and destination"}), 400
        
    date = parse_date(date_string) if date_string else datetime.datetime.now()
    
    try:
        routes = router.runRouter(src, dest, date, model_type)
        return jsonify({"routes": routes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_traffic():
    data = request.get_json()
    
    point = data.get('scats')
    date_string = data.get('datetime')
    model_type = data.get('model', TrafficFlowModelsEnum.LSTM.value)
    
    if not point:
        return jsonify({"error": "Please provide SCATS number"}), 400
        
    date = parse_date(date_string) if date_string else datetime.datetime.now()
    
    try:
        predictor = TrafficFlowPredictor()
        flow = predictor.predict_traffic_flow(point, date, 4, model_type)
        
        return jsonify({
            "scats": point,
            "datetime": date.strftime('%Y/%m/%d %I:%M:%S'),
            "prediction": flow,
            "unit": "veh/hr"
        })
    except ValueError:
        return jsonify({"error": "Invalid SCATS number"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    return jsonify({
        "models": [model.value for model in TrafficFlowModelsEnum]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
