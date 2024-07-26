# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 13:08:24 2024

@author: falko
"""

#"""
#This Script is the first attempt at using StreamLit to produce the questionnaire
#in an interactive format.
#"""
import streamlit as st
import pandas as pd
import pickle
#import pkg_resources
#pkg_resources.require("sklearn==1.2.2")
import sklearn
## Create the survey
# GitHub
def load_model_and_encoder():
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('encoder.pkl', 'rb') as encoder_file:
        encoder = pickle.load(encoder_file)
        # Ensure that the encoder has the 'transform' method
        if not hasattr(encoder, 'transform'):
            st.error("Loaded encoder does not have a 'transform' method. Check the pickle file.")
            st.stop()
    return model, encoder

model, encoder = load_model_and_encoder()

# Debug statements to verify the loaded objects
#st.write(f"Model type: {type(model)}")
#st.write(f"Encoder type: {type(encoder)}")


# Add debug statements
if hasattr(encoder, 'transform'):
    st.write("Model and encoder loaded successfully")

def survey_welcome():
    st.title("Carbon Footprint Questionnaire")

    st.write("""
             Hello you there, 
             
             this questionnaire helps you to figure out,
             what your current, monthly Carbon Footprint is.
             After that it will show you personilized options what you can do to improve it (To Do)
             
             Thank you for caring for the environment!
             """)
    
    if st.button("Start"):
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def survey_demo():
    st.title("Carbon Footprint Questionnaire")
    st.header("Demographics")

    height = st.number_input("Height (in cm):", min_value = 50, max_value = 270, value = 170)
    
    weight = st.number_input("Weight (in kg):", min_value = 30, max_value = 600, value = 70)
    
    sex = st.radio("Sex:", options = ["female", "male"], horizontal = True)
    
    diet = st.radio("What is your diet?", options = ["omnivore", "pescatarian", "vegetarian", "vegan"], horizontal = True)

    if st.button("Next"):
        
        bmi = weight/((height/100)**2)
    
        body_type = "";
        if bmi >= 30 :
            body_type = "obese"
        elif bmi >= 25:
            body_type = "overweight"
        elif bmi >= 18.5:
            body_type = "normal"
        else:
            body_type = "underweight"
        st.session_state['Body Type'] = body_type
        st.session_state['Sex'] = sex
        st.session_state['Diet'] = diet
        st.session_state['page'] = 'survey_life'
        st.rerun()
        

def survey_life():
    st.title("Carbon Footpint Questionnaire")
    st.header("Daily life")
    
    shower = st.radio("How often do you shower?", options = ["daily", "less frequently", "more frequently", "twice a day"], horizontal = True)
    social = st.radio("How often do you engage in social activities?", options = ["never","sometimes", "often",], horizontal = True)
    groceries = st.number_input("How much do you spend on groceries in a month (in Euro)?", min_value = 0, max_value = int(1e6), value = 0)
    clothes = st.number_input("How many new pieces of clothing do you buy in a month?", min_value = 0, max_value = int(1e6), value = 0)    
    wastebag_size = st.radio("Which size of trashbag are you using?", options = ["small", "medium", "large", "extra large"], horizontal = True)
    wastebag_count = st.number_input("How many bags of waste do you produce per week?", min_value = 0, max_value = int(1e6), value = 0)
    recycle = st.multiselect("Which of the following materials are you recycling?", options = ["Paper", "Plastic", "Glass","Metal"])
    tvpc = st.number_input("How many hours do you spend infront of the TV or PC per day?", min_value = 0, max_value = 24, value = 0)
    internet = st.number_input("How many hours do you use the internet per day?", min_value = 0, max_value = 24, value = 0)
    
    if st.button("Next"):
        st.session_state['How Often Shower'] = shower
        st.session_state['Social Activity'] = social
        st.session_state['Monthly Grocery Bill'] = groceries
        st.session_state['How Many New Clothes Monthly'] = clothes
        st.session_state['Waste Bag Size'] = wastebag_size
        st.session_state['Waste Bag Weekly Count'] = wastebag_count
        recycle_options = ["Paper", "Plastic", "Glass","Metal"]
        for rec in recycle_options:
            st.session_state['Recycling ' + rec] = 1 if rec in recycle else 0
        st.session_state['How Long TV PC Daily Hour'] = tvpc
        st.session_state['How Long Internet Daily Hour'] = internet
        
        st.session_state['page'] = 'survey_energy'
        st.rerun()
    if st.button("Back"):
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def survey_energy():
    st.title("Carbon Footpint Questionnaire")
    st.header("Energy efficiency")
    
    energy = st.radio("What is your main source of engery for heating?", options = ["coal", "electricity", "natural gas", "wood"], horizontal = True)
    cooking = st.multiselect("Which of the following appliances do you use for cooking?", options = ["Stove", "Oven", "Microwave", "Grill", "Airfryer"])
    energy_eff = st.radio("Would you consider your electric appliances as enegy efficient?", options = ["Yes", "No", "Sometimes"], horizontal = True)
    
    if st.button("Next"):
        st.session_state['Heating Energy Source'] = energy
        cooking_options = ["Stove", "Oven", "Microwave", "Grill", "Airfryer"]
        for cook in cooking_options:
            st.session_state['Cooking With ' + cook] = 1 if cook in cooking else 0
        st.session_state['Energy efficiency'] = energy_eff
        
        st.session_state['page'] ='survey_travel'
        st.rerun()
    if st.button("Back"):
        st.session_state['page'] = 'survey_life'
        st.rerun()
                

def survey_travel():
    st.title("Carbon Footpint Questionnaire")
    st.header("Travelling")
    
    transport = st.radio("What is your main method of transportation?", options = ["walk/bicycle", "public", "petrol", "diesel", "electric", "hybrid", "lpg"], horizontal = False)
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = 0)
    plane = st.radio("How often did you travel by plane in the last month?", options = ["never", "rarely", "frequently", "very frequently"], horizontal = True)

    if st.button("Next"):
         st.session_state['Transport'] = transport
         st.session_state['Vehicle Monthly Distance Km'] = km
         st.session_state['Frequency of Traveling by Air'] = plane
         
         st.session_state['page'] ='results'
         st.rerun()
    if st.button("Back"):
         st.session_state['page'] = 'survey_energy'
         st.rerun()


def results():
    model, encoder = load_model_and_encoder()

    st.title("Carbon Footpint Questionnaire")
    st.header("Results")
    
    varNames1 = ['Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
 'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
 'How Many New Clothes Monthly',  'How Long Internet Daily Hour',
 'Recycling Metal', 'Recycling Glass',
 'Recycling Paper', 'Recycling Plastic',
 'Cooking With Stove', 'Cooking With Microwave',
 'Cooking With Oven', 'Cooking With Airfryer',
 'Cooking With Grill']
    
    varNames2=['Body Type', 'Sex', 'Diet', 'How Often Shower', 'Heating Energy Source', 'Social Activity', 'Frequency of Traveling by Air', 'Waste Bag Size', 'Energy efficiency', 'Transport Vehicle Type']
    all_names = varNames1 + varNames2
    
    data = pd.DataFrame([[st.session_state['Monthly Grocery Bill'],
     st.session_state['Vehicle Monthly Distance Km'],
     st.session_state['Waste Bag Weekly Count'],
     st.session_state['How Long TV PC Daily Hour'],
     st.session_state['How Many New Clothes Monthly'],
     st.session_state['How Long Internet Daily Hour'],
     st.session_state['Recycling Metal'],
     st.session_state['Recycling Glass'],
     st.session_state['Recycling Paper'],
     st.session_state['Recycling Plastic'],
     st.session_state['Cooking With Stove'],
     st.session_state['Cooking With Microwave'],
     st.session_state['Cooking With Oven'],
     st.session_state['Cooking With Airfryer'],
     st.session_state['Cooking With Grill'],
     st.session_state['Body Type'],
     st.session_state['Sex'],
     st.session_state['Diet'],
     st.session_state['How Often Shower'],
     st.session_state['Heating Energy Source'],
     st.session_state['Social Activity'],
     st.session_state['Frequency of Traveling by Air'],
     st.session_state['Waste Bag Size'],
     st.session_state['Energy efficiency'],
     st.session_state['Transport']]], columns=all_names)
    
   # st.write(data[0])
   # st.write(encoder.feature_names_in_)
#    st.write('The scikit-learn version is {}.'.format(sklearn.__version__))
#    st.write(f"Data type: {type(data)}")
    
# Encode the categorical data
    try:
        X = encoder.transform(data)
        st.write(f"Data after encoding: {X}")
    except Exception as e:
        st.write(f"Error during encoding: {e}")
        st.write("Using toy example")
        X = [[0,1,0,1,0,0,1,0,0,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0,0,0,0,0,1,200,500,2,12,2,12,1,1,1,1,1,0,1,0,0]]
    
    
   #  X = encoder.transform(data)
    #st.write(X)
    #st.write(model.coef_)
    
    try:
        prediction = model.predict(X)
       # st.write("Prediction:", prediction[0])
    except Exception as e:
        st.error(f"Error during prediction: {e}")

    
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(prediction[0])) + " " + unit.translate(SUB))
    #st.write(str(round(prediction[0])))
    
    
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'survey_welcome'  

    if st.session_state['page'] == 'survey_welcome':
        survey_welcome()
    elif st.session_state['page'] == 'survey_demo':
        survey_demo()
    elif st.session_state['page'] == 'survey_life':
        survey_life()
    elif st.session_state['page'] == 'survey_energy':
        survey_energy()
    elif st.session_state['page'] == 'survey_travel':
        survey_travel()
    elif st.session_state['page'] == 'results':
        results()

if __name__ == '__main__':
 #   st.write("App started")
    main()
    