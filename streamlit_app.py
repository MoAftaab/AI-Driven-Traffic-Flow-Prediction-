import streamlit as st
import requests
import datetime

st.title('Traffic Flow Prediction System')

# Input fields for route generation
st.header('Generate Routes')
model = st.selectbox('Model', ['LSTM', 'RNN', 'GRU'])
src = st.text_input('Source SCATS')
dest = st.text_input('Destination SCATS')
date = st.text_input('Date/Time (YYYY/MM/DD HH:MM)', value=datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
enable_incidents = st.checkbox('Enable Traffic Incident Simulation', value=True)

if st.button('Generate Routes'):
    if not src or not dest:
        st.error("Please enter SCATS")
    else:
        st.write("Generating Routes...")
        response = requests.post('http://127.0.0.1:5000/generate_routes', data={
            'src': src,
            'dest': dest,
            'date': date,
            'model': model,
            'enable_incidents': enable_incidents
        })
        data = response.json()
        if 'error' in data:
            st.error(data['error'])
        else:
            st.text_area('Routes', value=data['routes'], height=200)
            if data['incidents']:
                st.subheader('Active Incidents')
                for incident in data['incidents']:
                    st.write(f"**{incident['type']}**: {incident['description']} ({incident['duration']} hrs)")

# Input fields for traffic flow prediction
st.header('Predict SCATS Traffic Flow')
point = st.text_input('SCATS Point')
if st.button('Predict Traffic Flow'):
    if not point:
        st.error("Please enter SCATS")
    else:
        st.write("Predicting...")
        response = requests.post('http://127.0.0.1:5000/predict_flow', data={
            'point': point,
            'date': date,
            'model': model
        })
        data = response.json()
        if 'error' in data:
            st.error(data['error'])
        else:
            st.text_area('Prediction', value=f"--Predicted Traffic Flow--\nSCATS:\t\t{data['scats']}\nTime:\t\t{data['time']}\nPrediction:\t\t{data['prediction']}", height=100)
