"""
Processing the data
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def process_data(train, test, lags):
    """Process data
    Reshape and split train\test data.

    # Arguments
        train: String, name of .csv train file.
        test: String, name of .csv test file.
        lags: integer, time lag.
    # Returns
        X_train: ndarray.
        y_train: ndarray.
        X_test: ndarray.
        y_test: ndarray.
        scaler: StandardScaler.
    """
    lane_flow_attr = 'Lane 1 Flow (Veh/5 Minutes)'

    df1 = pd.read_csv(train, encoding='utf-8').fillna(0)
    df2 = pd.read_csv(test, encoding='utf-8').fillna(0)

    flow_scaler = MinMaxScaler(feature_range=(0, 1)).fit(df1[lane_flow_attr].values.reshape(-1, 1))
    flow1 = flow_scaler.transform(df1[lane_flow_attr].values.reshape(-1, 1)).reshape(1, -1)[0]
    flow2 = flow_scaler.transform(df2[lane_flow_attr].values.reshape(-1, 1)).reshape(1, -1)[0]

    train, test, data = [], [], []
    for i in range(lags, len(flow1)):
        row = [*flow1[i - lags: i],flow1[i]]
        train.append(row)
        data.append(row)

    for i in range(lags, len(flow2)):
        row = [*flow2[i - lags: i],flow2[i]]
        test.append(row)
        data.append(row)

    data = np.array(data)
    train = np.array(train)
    test = np.array(test)
    np.random.shuffle(train)

    X = data[:, :-1]
    y = data[:,-1]

    X_train = train[:, :-1]
    y_train = train[:, -1]

    X_test = test[:, :-1]
    y_test = test[:, -1]

    return X_train, y_train, X_test, y_test, X,y,flow_scaler
