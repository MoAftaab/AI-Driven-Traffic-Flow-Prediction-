import tensorflow as tf
import os

def remove_time_major_from_config(model_path):
    """Remove time_major parameter from GRU layer configs in saved model."""
    model = tf.keras.models.load_model(model_path)
    
    # Get the config
    config = model.get_config()
    
    # For each layer in the model
    for layer in config['layers']:
        # If it's a GRU layer
        if layer['class_name'] == 'GRU':
            # Remove time_major if it exists in the config
            if 'time_major' in layer['config']:
                del layer['config']['time_major']
    
    # Create new model from modified config
    new_model = tf.keras.Model.from_config(config)
    # Copy weights from old model to new model
    new_model.set_weights(model.get_weights())
    # Save the modified model back to the same location
    new_model.save(model_path)

def fix_all_gru_models():
    """Fix all GRU models in the project."""
    base_dir = 'TrafficData'
    model_dirs = [
        os.path.join(base_dir, 'SingleModelScats/model'),
        os.path.join(base_dir, 'ModelPerScats/model/location_models')
    ]
    
    for model_dir in model_dirs:
        if os.path.exists(model_dir):
            for file in os.listdir(model_dir):
                if file.endswith('.h5') and 'gru' in file.lower():
                    model_path = os.path.join(model_dir, file)
                    print(f"Fixing model: {model_path}")
                    try:
                        remove_time_major_from_config(model_path)
                        print(f"Successfully fixed {file}")
                    except Exception as e:
                        print(f"Error fixing {file}: {str(e)}")

if __name__ == '__main__':
    fix_all_gru_models()
