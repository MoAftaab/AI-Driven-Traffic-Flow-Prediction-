from flask import Flask, render_template_string, render_template, request, jsonify
import datetime 
import os
import csv
from TrafficData.TrafficFlowPredictor import TrafficFlowPredictor, TrafficFlowModelsEnum
import route_finding as router

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Route Navigation</title>
        <style>
            body { 
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container { 
                width: 400px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .form-group { 
                margin-bottom: 15px; 
            }
            label { 
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select { 
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #45a049;
            }
            textarea { 
                width: 100%;
                height: 150px;
                padding: 8px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                resize: vertical;
                font-family: monospace;
            }
            h1, h2 {
                color: #333;
                text-align: center;
            }
            .loading {
                color: #666;
                text-align: center;
                font-style: italic;
            }
            .error {
                color: #ff0000;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Route Navigation</h1>
            <div class="form-group">
                <label for="model">Model:*</label>
                <select id="model">
                    <option value="LSTM">LSTM</option>
                    <option value="RNN">RNN</option>
                    <option value="GRU">GRU</option>
                </select>
            </div>
            <div class="form-group">
                <label for="src">Source:*</label>
                <input type="text" id="src" placeholder="Enter source SCATS">
            </div>
            <div class="form-group">
                <label for="dest">Destination:*</label>
                <input type="text" id="dest" placeholder="Enter destination SCATS">
            </div>
            <div class="form-group">
                <label for="date">Date/Time (YYYY/MM/DD HH:MM):</label>
                <input type="text" id="date" placeholder="e.g., 2024/02/01 14:30">
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="enableIncidents" checked>
                    Enable Traffic Incident Simulation
                </label>
            </div>
            <div id="activeIncidents" style="margin-bottom: 15px; display: none;">
                <label>Active Incidents:</label>
                <div style="background-color: #f8f8f8; padding: 10px; border-radius: 4px; margin-top: 5px;">
                    <ul id="incidentsList" style="margin: 0; padding-left: 20px;"></ul>
                </div>
            </div>
            <button onclick="generateRoutes()" id="generateBtn">Generate Routes</button>
            <button onclick="viewRoutes()">View Routes</button>
            <textarea id="routesText" readonly></textarea>
            
            <h2>Predict SCATS Traffic Flow</h2>
            <div class="form-group">
                <label for="point">SCATS Point:*</label>
                <input type="text" id="point" placeholder="Enter SCATS point">
            </div>
            <button onclick="predictFlow()" id="predictBtn">Predict Traffic Flow</button>
            <textarea id="predictionText" readonly></textarea>
        </div>

        <script>
            function generateRoutes() {
                const src = document.getElementById('src').value;
                const dest = document.getElementById('dest').value;
                const date = document.getElementById('date').value;
                const model = document.getElementById('model').value;
                const enableIncidents = document.getElementById('enableIncidents').checked;
                
                if (!src || !dest) {
                    document.getElementById('routesText').value = "Please enter SCATS";
                    return;
                }

                document.getElementById('routesText').value = "Generating Routes...";
                document.getElementById('generateBtn').disabled = true;

                fetch('/generate_routes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `src=${encodeURIComponent(src)}&dest=${encodeURIComponent(dest)}&date=${encodeURIComponent(date)}&model=${encodeURIComponent(model)}&enable_incidents=${enableIncidents}`
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('routesText').value = data.error || data.routes;
                    document.getElementById('generateBtn').disabled = false;
                    
                    // Update incidents display
                    const incidentsDiv = document.getElementById('activeIncidents');
                    const incidentsList = document.getElementById('incidentsList');
                    
                    if (data.incidents && data.incidents.length > 0) {
                        incidentsList.innerHTML = data.incidents.map(incident => 
                            `<li><strong>${incident.type}</strong>: ${incident.description} (${incident.duration} hrs)</li>`
                        ).join('');
                        incidentsDiv.style.display = 'block';
                    } else {
                        incidentsDiv.style.display = 'none';
                    }
                })
                .catch(error => {
                    document.getElementById('routesText').value = "An error occurred while generating routes.";
                    document.getElementById('generateBtn').disabled = false;
                });
            }

            function viewRoutes() {
                window.open('/routes', '_blank');
            }

            function predictFlow() {
                const point = document.getElementById('point').value;
                const date = document.getElementById('date').value;
                const model = document.getElementById('model').value;

                if (!point) {
                    document.getElementById('predictionText').value = "Please enter SCATS";
                    return;
                }

                document.getElementById('predictionText').value = "Predicting...";
                document.getElementById('predictBtn').disabled = true;

                fetch('/predict_flow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `point=${encodeURIComponent(point)}&date=${encodeURIComponent(date)}&model=${encodeURIComponent(model)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('predictionText').value = data.error;
                    } else {
                        document.getElementById('predictionText').value = 
                            `--Predicted Traffic Flow--\nSCATS:\t\t${data.scats}\nTime:\t\t${data.time}\nPrediction:\t\t${data.prediction}`;
                    }
                    document.getElementById('predictBtn').disabled = false;
                })
                .catch(error => {
                    document.getElementById('predictionText').value = "An error occurred while predicting traffic flow.";
                    document.getElementById('predictBtn').disabled = false;
                });
            }

            // Set default date/time
            window.onload = function() {
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                document.getElementById('date').value = `${year}/${month}/${day} ${hours}:${minutes}`;
            };
        </script>
    </body>
    </html>
    ''')

# Initialize predictor
predictor = None

@app.route('/generate_routes', methods=['POST'])
def generate_routes():
    src = request.form['src']
    dest = request.form['dest']
    date_string = request.form['date']
    model = request.form['model']
    enable_incidents = request.form.get('enable_incidents', 'true') == 'true'

    if not src or not dest:
        return jsonify({"error": "Please enter SCATS"})

    try:
        date = parse_date(date_string) if date_string else datetime.datetime.now()
    except ValueError:
        date = datetime.datetime.now()

    try:
        # Load router on-demand
        routes = router.runRouter(src, dest, date, model, enable_incidents)
        
        # Get active incidents info
        from data.traffic_incidents import incident_simulator
        active_incidents = incident_simulator.get_active_incidents(date)
        incidents_info = [{
            'type': incident.incident_type.value,
            'description': incident.description,
            'duration': f"{incident.duration.total_seconds()/3600:.1f}"
        } for incident in active_incidents] if enable_incidents else []
        
        return jsonify({
            "routes": routes,
            "incidents": incidents_info
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/predict_flow', methods=['POST'])
def predict_flow():
    global predictor
    point = request.form['point']
    date_string = request.form['date']
    model = request.form['model']

    if not point:
        return jsonify({"error": "Please enter SCATS"})

    try:
        date = parse_date(date_string) if date_string else datetime.datetime.now()
    except ValueError:
        date = datetime.datetime.now()

    try:
        # Initialize predictor on first use
        if predictor is None:
            predictor = TrafficFlowPredictor()
        
        flow = predictor.predict_traffic_flow(point, date, 4, model)
        return jsonify({
            "scats": point,
            "time": date.strftime('%Y/%m/%d %I:%M:%S'),
            "prediction": f"{flow} veh/hr"
        })
    except Exception as e:
        return jsonify({"error": "Invalid SCATS"})

def parse_date(date_string):
    date, time = date_string.split()
    year, month, day = map(int, date.split('/'))
    hour, minute = map(int, time.split(':'))
    return datetime.datetime(year, month, day, hour, minute)

@app.route('/routes')
def view_routes():
    try:
        # Read traffic network data
        scats_data = {}
        if os.path.exists('data/traffic_network2.csv'):
            with open('data/traffic_network2.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    scats_data[row['SCATS Number']] = {
                        'lat': float(row['Latitude']),
                        'lng': float(row['Longitude']),
                        'name': row['Site Description']
                    }
        else:
            # Use default values for demonstration
            scats_data = {
                "3001": {"lat": -37.831219, "lng": 145.056965, "name": "Default Location"}
            }
        
        return render_template('routes.html', scats_data=scats_data)
    except Exception as e:
        return jsonify({"error": f"Error loading routes: {str(e)}"}), 500

if __name__ == '__main__':
    print(" * Running on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
