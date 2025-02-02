# AI-Driven Traffic Flow Prediction System 🚗

## Overview

The AI-Driven Traffic Flow Prediction System is an advanced traffic management solution that uses machine learning to predict traffic flow patterns and recommend optimal routes. Built with Python and Flask, this system helps users navigate through traffic by providing real-time predictions and alternative route suggestions based on historical traffic data and current conditions.

![Traffic Flow Prediction](visualizations/WhatsApp%20Image%202025-02-03%20at%2000.20.45_1b4df089.jpg)
![Predict Traffic Flow Prediction](visualizations/WhatsApp%20Image%202025-02-03%20at%2000.21.46_f725d950.jpg)


## Features

### 🎯 Core Features

- **Real-time Traffic Flow Prediction**
  - Uses LSTM (Long Short-Term Memory) neural networks
  - Adapts to time-of-day and day-of-week patterns
  - Provides accurate vehicle flow predictions

- **Intelligent Route Planning**
  - A* pathfinding algorithm for optimal route discovery
  - Multiple route suggestions with ETA
  - Traffic incident awareness and rerouting

- **Interactive Visualization**
  - Real-time route mapping
  - Traffic density heatmaps
  - Interactive network graphs

### 🛠 Technical Features

- **Multiple ML Models Support**
  - LSTM (Long Short-Term Memory)
  - GRU (Gated Recurrent Unit)
  - RNN (Recurrent Neural Network)

- **Traffic Incident Simulation**
  - Random incident generation
  - Impact analysis on traffic flow
  - Duration-based effect modeling

- **Web Interface**
  - User-friendly Flask web application
  - Real-time updates
  - Interactive map visualization

## Technology Stack

- **Backend**: Python, Flask
- **Machine Learning**: TensorFlow, Keras
- **Data Processing**: NumPy, Pandas
- **Visualization**: Folium, Matplotlib
- **Containerization**: Docker

## Installation

### Prerequisites

- Python 3.9+
- Docker (optional)
- Git

### Using Docker (Recommended)

1. Clone your repository:
```bash
git clone https://github.com/MoAftaab/AI-Driven-Traffic-Flow-Prediction.git
cd Traffic-Flow-Prediction-System
```

2. Build and run with Docker:
```bash
docker build -t traffic-flow-prediction .
docker run -p 5000:5000 traffic-flow-prediction
```

3. Access the application at `http://localhost:5000`

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/MoAftaab/AI-Driven-Traffic-Flow-Prediction-.git
cd Traffic-Flow-Prediction-System
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r visualization_requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:5000`

## Usage

1. **Predict Traffic Flow**
   - Enter a SCATS point number
   - Select the prediction model (LSTM/GRU/RNN)
   - View the predicted traffic flow

2. **Generate Routes**
   - Enter source and destination SCATS points
   - Enable/disable traffic incident simulation
   - View multiple route options with ETAs


3. **View Visualizations**
   - Click "View Routes" to see the route map
   - Check traffic incident impacts
   - Analyze traffic patterns

## 🚦 Traffic Incident Simulation
**Purpose**: Simulates traffic incidents to analyze their impact on traffic flow and route planning.

**How to Enable**:
On the main page, check the **"Enable Traffic Incident Simulation"** checkbox before generating routes.  
The application will display active incidents and their effects on the suggested routes.

**Functionality**:
- Randomly generates traffic incidents that can affect the predicted traffic flow.  
- Provides users with updated route suggestions based on current traffic conditions and incidents.


## Project Structure

```
Traffic-Flow-Prediction-System/
├── app.py                 # Main Flask application
├── route_finding.py       # Route optimization algorithms
├── TrafficData/          # ML models and predictors
├── data/                 # Traffic network data
├── static/              # Static files (CSS, JS)
├── templates/           # HTML templates
├── visualizations/     # Generated visualizations
└── requirements.txt    # Python dependencies
```

## Screenshots

![Web Interface](visualizations/WhatsApp%20Image%202025-02-01%20at%2015.51.26_8887e16d.jpg)
*Interactive web interface*

![Traffic Heatmap](visualizations/WhatsApp%20Image%202025-02-01%20at%2015.51.57_7523c7c7.jpg)
*Traffic Map Route View*



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on SCATS (Sydney Coordinated Adaptive Traffic System) data
- Inspired by modern traffic management systems
- Uses advanced machine learning techniques for prediction

## Contact

- GitHub: [@MoAftaab](https://github.com/MoAftaab)
