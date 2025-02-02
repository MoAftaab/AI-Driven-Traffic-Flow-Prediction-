from enum import Enum
from time import time
import warnings
import numpy as np
import string
import os
import datetime
import math

from sklearn.preprocessing import MinMaxScaler
from TrafficData.SingleModelScats.data.data import process_data_datetime,process_data_series
from tensorflow.keras.losses import MeanSquaredError
from fix_model import load_model_without_time_major
warnings.filterwarnings("ignore")

def custom_load_model(path):
    return load_model_without_time_major(path)

class TrafficFlowModelsEnum(Enum):
    LSTM = 'lstm'
    GRU = 'gru'
    SAES = 'saes'
    NEW_SAES = 'new_saes'
    RNN = 'rnn'
    AVERAGE = 'average'


class TrafficFlowPredictor():
    def __init__(self):
        self.models = {}

        self.flow_scaler:MinMaxScaler = None
        self.days_scaler:MinMaxScaler = None
        self.scats_scaler:MinMaxScaler = None
        self.times_scaler:MinMaxScaler = None
        
        self.lags = 12 # must match whatever the models were trained on

        self.file1 = os.path.join(os.path.dirname(__file__),'SingleModelScats','data','train-data.csv')
        self.file2 = os.path.join(os.path.dirname(__file__),'SingleModelScats','data','test-data.csv')

        self.get_scalars()
        self.get_lookup_data()
        
        self.location_series_data = {}

    def get_model(self,model_name:string):
        try:
            if self.models.get(model_name) == None:
                model_path = os.path.join(os.path.dirname(__file__),'SingleModelScats','model',f'{model_name}.h5')
                if os.path.exists(model_path):
                    self.models[model_name] = custom_load_model(model_path)
                else:
                    print(f"Model file not found: {model_path}")
                    return None
            return self.models.get(model_name)
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None

    def get_default_prediction(self):
        # Return a reasonable default prediction when model is not available
        return 400  # Average flow rate
    
    def get_scalars(self):
        try:
            if os.path.exists(self.file1) and os.path.exists(self.file2):
                _, _, _, _,_,_,_,_,self.flow_scaler, self.scats_scaler,self.days_scaler,self.times_scaler = process_data_datetime(self.file1, self.file2)
            else:
                print("Training data files not found. Using default scalers.")
                self.flow_scaler = MinMaxScaler()
                self.scats_scaler = MinMaxScaler()
                self.days_scaler = MinMaxScaler()
                self.times_scaler = MinMaxScaler()
                # Fit with some reasonable default ranges
                self.flow_scaler.fit([[0], [800]])  # Flow range 0-800
                self.scats_scaler.fit([[0], [5000]])  # SCATS number range
                self.days_scaler.fit([[0], [6]])  # Days 0-6
                self.times_scaler.fit([[0], [1439]])  # Minutes in a day (0-1439)
        except Exception as e:
            print(f"Error loading scalers: {str(e)}. Using default values.")

    def get_lookup_data(self):
        try:
            if os.path.exists(self.file1) and os.path.exists(self.file2):
                _, _, _, _,self.series_data,_,_,_,_,_ = process_data_series(self.file1, self.file2,self.lags)
            else:
                print("Training data files not found. Using empty series data.")
                self.series_data = []
        except Exception as e:
            print(f"Error loading lookup data: {str(e)}. Using empty series data.")
            self.series_data = []
        
        
    def predict_traffic_flow(self,location: int,date: datetime,steps:int,model_name: string):
        model = self.get_model(model_name)
        
        if model is None:
            # Use default prediction when model is not available
            return self.get_default_prediction() * steps
            
        X = None
        if model_name == "average":
            X = self.get_datetime_inputs(location,date,steps)
            if X is None: return 0
            y_pred = self.predict_datetime(model,X)
        else:
            X = self.get_timeseries_inputs(location,date,steps)
            if X is None: return 0
            y_pred = self.predict_series(model,X)
        
        return y_pred.sum()

    def get_datetime_inputs(self,location: int,date:datetime,steps:int):
        dayindex = date.weekday() # determine weekday
        actual_time = date.hour * 60 + date.minute # determine time in minutes
        rounded_time = 15 * math.floor(actual_time / 15) # get current 15 minute interval

        days = self.days_scaler.transform(np.array([dayindex for _ in range(steps)]).reshape(-1,1)).reshape(1,-1)[0]
        times = self.times_scaler.transform(np.array([actual_time + t*15 for t in range(steps)]).reshape(-1,1)).reshape(1,-1)[0]
        scats = self.scats_scaler.transform(np.array([location for _ in range(steps)]).reshape(-1,1)).reshape(1,-1)[0]

        X = np.array([np.array([days[i],times[i],scats[i]]) for i in range(steps)])
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X

    def predict_datetime(self,model,X):
        y_pred = model.predict(X)
        y_pred = self.flow_scaler.inverse_transform(y_pred.reshape(-1, 1)).reshape(1, -1)[0]
        return y_pred

    def lookup_location_data(self,location:int):
        scaled_location = self.scats_scaler.transform(np.array([location]).reshape(-1,1)).reshape(1,-1)[0][0]
        if self.location_series_data.get(location) is None:
            location_indices = [i for i in range(len(self.series_data)) if self.series_data[i][self.lags] == scaled_location]
            self.location_series_data[location] = self.series_data[location_indices]
    
        return self.location_series_data[location]
        
    def get_timeseries_inputs(self,location: int,date:datetime,steps:int):
        day = date.day
        actual_time = date.hour * 60 + date.minute # determine time in minutes
        rounded_time = 15 * math.floor(actual_time / 15) # get current 15 minute interval
        time_index = int(rounded_time / 15)
        
        location_X = self.lookup_location_data(location)
        if len(location_X) == 0:
            raise Exception(f"No Data exists for location {location}")
        
        day_X = location_X[(day-1)*96:day*96]
        
        # fix for bad data having incomplete days
        while len(day_X) == 0 and day >= 0:
            day -= 7
            day_X = location_X[(day-1)*96:day*96]

        if len(day_X) == 0:
            return None

        # Handle case where time_index + steps would exceed array bounds
        available_steps = min(steps, len(day_X) - time_index)
        if available_steps <= 0:
            return None
            
        X = np.array([day_X[time_index + i] for i in range(available_steps)])
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        return X

    def predict_series(self,model,X):
        y_pred = model.predict(X)
        y_pred = self.flow_scaler.inverse_transform(y_pred.reshape(-1, 1)).reshape(1, -1)[0]
        return y_pred
