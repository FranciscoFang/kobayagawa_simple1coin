import tensorflow as tf
import keras

def make_draw_model():
    model_draw = tf.keras.models.Sequential()
    model_draw.add(tf.keras.layers.InputLayer(input_shape=(28,)))
    model_draw.add(tf.keras.layers.Dense(15, activation='relu'))
    model_draw.add(tf.keras.layers.Dense(8, activation='relu'))
    model_draw.add(tf.keras.layers.Dense(1, activation='linear'))
    model_draw.compile(optimizer="adam", loss=tf.keras.losses.BinaryCrossentropy(), metrics=["accuracy"])
    # model_draw.summary()
    return model_draw
    
def make_discard_model():
    model_discard = tf.keras.models.Sequential()
    model_discard.add(tf.keras.layers.InputLayer(input_shape=(28,)))
    model_discard.add(tf.keras.layers.Dense(15, activation='relu'))
    model_discard.add(tf.keras.layers.Dense(8, activation='relu'))
    model_discard.add(tf.keras.layers.Dense(1, activation='linear'))
    model_discard.compile(optimizer="adam", loss=tf.keras.losses.BinaryCrossentropy(), metrics=["accuracy"])
    model_discard.summary()
    return model_discard
    
def make_bet_model():    
    model_bet = tf.keras.models.Sequential()
    model_bet.add(tf.keras.layers.InputLayer(input_shape=(28,)))
    model_bet.add(tf.keras.layers.Dropout(0.1))
    model_bet.add(tf.keras.layers.Dense(15, activation='relu'))
    model_bet.add(tf.keras.layers.Dropout(0.1))
    model_bet.add(tf.keras.layers.Dense(8, activation='relu'))
    model_bet.add(tf.keras.layers.Dense(1, activation='linear'))
    model_bet.compile(optimizer="adam", loss=tf.keras.losses.BinaryCrossentropy(), metrics=["accuracy"])
    # model_bet.summary()
    return model_bet