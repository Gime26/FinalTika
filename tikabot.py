import random, json, pickle, nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import load_model


data_file = open('intents_spanish.json', 'r', encoding='utf-8').read()
intents = json.loads(data_file)
try:
    model = load_model('chatbot_model.h5')
except FileNotFoundError:
    print("ADVERTENCIA: No se encontró 'chatbot_model.h5'. ¡Ejecuta entrenamiento.py primero!")
    model = None

try:
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
except FileNotFoundError:
    print("ADVERTENCIA: No se encontraron los archivos .pkl. ¡Ejecuta entrenamiento.py primero!")
    words = []
    classes = []

lemmatizer = WordNetLemmatizer()


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag=[0]* len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    if not model or not words or not classes:
        return [{'intent': 'saludo', 'probability': 1.0}] 
    bow= bag_of_words(sentence)
    res= model.predict(np.array([bow])) [0]
    ERROR_THRESHOLD= 0.25
    results= [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key= lambda x: x[1], reverse=True)
    return_list =[]
    for r in results:
        return_list.append({'intent': classes[r[0]],'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    if not intents_list:
        return "Disculpa, no entendí tu pregunta. ¿Podrías reformularla?"
    tag= intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    result="Disculpa, no puedo procesar esa solicitud"
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result
