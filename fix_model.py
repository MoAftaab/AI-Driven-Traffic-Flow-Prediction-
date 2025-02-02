import tensorflow as tf
from tensorflow.keras.layers import GRU as BaseGRU, SimpleRNN as BaseRNN, LSTM as BaseLSTM

class CustomGRU(BaseGRU):
    def __init__(self, *args, **kwargs):
        # Remove time_major if present
        kwargs.pop('time_major', None)
        super().__init__(*args, **kwargs)

class CustomSimpleRNN(BaseRNN):
    def __init__(self, *args, **kwargs):
        # Remove time_major if present
        kwargs.pop('time_major', None)
        super().__init__(*args, **kwargs)

class CustomLSTM(BaseLSTM):
    def __init__(self, *args, **kwargs):
        # Remove time_major if present
        kwargs.pop('time_major', None)
        super().__init__(*args, **kwargs)

# Register the custom layers
tf.keras.utils.get_custom_objects().update({
    'GRU': CustomGRU,
    'SimpleRNN': CustomSimpleRNN,
    'LSTM': CustomLSTM
})

# Now modify the load_model function to use this custom layer
def load_model_without_time_major(model_path):
    """Load model with custom GRU layer that ignores time_major parameter."""
    return tf.keras.models.load_model(
        model_path,
        custom_objects={
            'GRU': CustomGRU,
            'SimpleRNN': CustomSimpleRNN,
            'LSTM': CustomLSTM,
            'mse': tf.keras.losses.MeanSquaredError()
        }
    )

if __name__ == '__main__':
    # Add this to TrafficFlowPredictor.py at the top with other imports:
    # from fix_model import load_model_without_time_major
    
    print("Custom GRU layer has been registered.")
    print("Update TrafficFlowPredictor.py to use load_model_without_time_major instead of load_model")
