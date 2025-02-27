from flask import Flask, render_template, request, jsonify
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)

# Load the dataset and create mappings
df = pd.read_excel('HealthMate Dataset.xlsx')
symptoms = df.columns[:-2]
diseases = df['prognosis'].unique()

disease_to_symptoms = {}
for disease in diseases:
    disease_symptoms = df[df['prognosis'] == disease].iloc[:, :-2].values.flatten()
    disease_to_symptoms[disease] = [symptoms[i] for i, val in enumerate(disease_symptoms) if val == 1]

symptom_to_diseases = {}
for symptom in symptoms:
    symptom_to_diseases[symptom] = df[df[symptom] == 1]['prognosis'].unique().tolist()

@app.route('/')
def index():
    return render_template('index.html', symptoms=symptoms)

@app.route('/get_second_options', methods=['POST'])
def get_second_options():
    first_symptom = request.form['first_symptom']
    second_options = get_second_dropdown_options(first_symptom)
    return jsonify({'second_options': second_options})

@app.route('/get_third_options', methods=['POST'])
def get_third_options():
    first_symptom = request.form['first_symptom']
    second_symptom = request.form['second_symptom']
    third_options = get_third_dropdown_options(first_symptom, second_symptom)
    return jsonify({'third_options': third_options})

# Enable CORS for the Flask app
CORS(app)

@app.route('/predict', methods=['POST']) 
def predict():
    selected_symptoms = request.form.getlist('selected_symptoms')
    predicted_diseases = predict_disease(selected_symptoms)
    
    # Get the specialized fields for the predicted diseases
    specialized_fields = []
    for disease in predicted_diseases:
        field = df[df['prognosis'] == disease]['Specialized Field'].values[0]
        specialized_fields.append(field)
    
    return jsonify({
        'predicted_diseases': predicted_diseases,
        'specialized_fields': specialized_fields
    })

def get_second_dropdown_options(first_symptom):
    related_diseases = symptom_to_diseases[first_symptom]
    second_symptoms = set()
    for disease in related_diseases:
        second_symptoms.update(disease_to_symptoms[disease])
    second_symptoms.discard(first_symptom)
    return list(second_symptoms)

def get_third_dropdown_options(first_symptom, second_symptom):
    related_diseases = set(symptom_to_diseases[first_symptom]).intersection(symptom_to_diseases[second_symptom])
    third_symptoms = set()
    for disease in related_diseases:
        third_symptoms.update(disease_to_symptoms[disease])
    third_symptoms.discard(first_symptom)
    third_symptoms.discard(second_symptom)
    return list(third_symptoms)

def predict_disease(selected_symptoms):
    possible_diseases = set(diseases)
    for symptom in selected_symptoms:
        possible_diseases.intersection_update(symptom_to_diseases[symptom])
    return list(possible_diseases)

if __name__ == '__main__':
    PORT=os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=PORT)
