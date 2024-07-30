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
import numpy as np
import pickle
import sklearn

st.write(sklearn.__version__)

## Create the survey
#LOCAL
#streamlit run D:\TechLabs\StreamLitApp_Kopie\CarbonFootprint_stApp.py
# Function to load model and encoder, cached using st.cache_resource
# GitHub
@st.cache_resource
def load_model_and_encoder():
    #path = os.path.dirname(__file__)
    #path = "D:\TechLabs\StreamLitApp_Kopie"
    with open('model2.pkl', 'rb') as f:
        model_f = pickle.load(f)
    with open('encoder2.pkl', 'rb') as f:
        encoder_f = pickle.load(f)
    return model_f, encoder_f


# def load_model_and_encoder():
#     with open(path +'\model.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open(path +'\encoder.pkl', 'rb') as encoder_file:
#         encoder = pickle.load(encoder_file)
#     return model, encoder

model, encoder = load_model_and_encoder()

# Debug statements to verify the loaded objects
st.write(f"Model type: {type(model)}")
st.write(f"Encoder type: {type(encoder)}")

# Ensure that the encoder has the 'transform' method
if not hasattr(encoder, 'transform'):
    st.error("Loaded encoder does not have a 'transform' method. Check the pickle file.")



# Add debug statements
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
        st.session_state['Body_Type'] = body_type
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
        st.session_state['How_Often_Shower'] = shower
        st.session_state['Social_Activity'] = social
        st.session_state['Monthly_Grocery_Bill'] = groceries
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Waste_Bag_Size'] = wastebag_size
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        recycle_options = ["Paper", "Plastic", "Glass","Metal"]
        for rec in recycle_options:
            st.session_state['Recycling_' + rec] = 1 if rec in recycle else 0
        st.session_state['How_Long_TV_PC_Daily_Hour'] = tvpc
        st.session_state['How_Long_Internet_Daily_Hour'] = internet
        
        st.session_state['page'] = 'survey_energy'
        st.rerun()
    if st.button("Back"):
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def survey_energy():
    st.title("Carbon Footpint Questionnaire")
    st.header("Energy efficiency")
    
    energy = st.radio("What is your main source of engery for heating?", options = ["coal", "electricity", "natural gas", "wood"], horizontal = True)
    cooking = st.multiselect("Which of the following appliances do you use for cooking?", options = ["Stove", "Oven", "Microwave", "Grill"])
    energy_eff = st.radio("Would you consider your electric appliances as enegy efficient?", options = ["Yes", "No", "Sometimes"], horizontal = True)
    
    if st.button("Next"):
        st.session_state['Heating_Energy_Source'] = energy
        cooking_options = ["Stove", "Oven", "Microwave", "Grill"]
        for cook in cooking_options:
            st.session_state['Cooking_With_' + cook] = 1 if cook in cooking else 0
        st.session_state['Energy_efficiency'] = energy_eff
        
        st.session_state['page'] ='survey_travel'
        st.rerun()
    if st.button("Back"):
        st.session_state['page'] = 'survey_life'
        st.rerun()
                

def survey_travel():
    st.title("Carbon Footpint Questionnaire")
    st.header("Travelling")
    
    transport = st.radio("What is your main method of transportation?", options = ["walk/bicycle", "public transport", "car (type: petrol)", "car (type: diesel)", "car (type: electric)", "car (type: hybrid)", "car (type: lpg)"], horizontal = False)
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = 0)
    plane = st.radio("How often did you travel by plane in the last month?", options = ["never", "rarely", "frequently", "very frequently"], horizontal = True)

    if st.button("Show Results"):
         st.session_state['Transport'] = transport
         st.session_state['Vehicle_Monthly_Distance_Km'] = km
         st.session_state['Frequency_of_Traveling_by_Air'] = plane
         
         st.session_state['page'] ='results'
         st.rerun()
    if st.button("Back"):
         st.session_state['page'] = 'survey_energy'
         st.rerun()


def results():
    st.title("Carbon Footpint Questionnaire")
    st.header("Results")
    
    ordinalVar=['Body_Type', 'Diet', 'How_Often_Shower', 'Social_Activity','Frequency_of_Traveling_by_Air', 
                'Waste_Bag_Size', 'Energy_efficiency']
    dummyVar=['Sex', 'Heating_Energy_Source','Transport_Vehicle_Type']
    numVar = ['Monthly_Grocery_Bill','Vehicle_Monthly_Distance_Km', 'Waste_Bag_Weekly_Count', 'How_Long_TV_PC_Daily_Hour',
              'How_Many_New_Clothes_Monthly',  'How_Long_Internet_Daily_Hour']
    restVar = ['Recycling_Glass','Recycling_Metal', 
               'Recycling_Plastic', 'Recycling_Paper',
               'Cooking_With_Oven', 'Cooking_With_Stove', 
               'Cooking_With_Grill','Cooking_With_Microwave']

    all_names = ordinalVar + dummyVar + numVar + restVar
    
    data = pd.DataFrame([[st.session_state['Body_Type'],
     st.session_state['Diet'],
     st.session_state['How_Often_Shower'],
     st.session_state['Social_Activity'],
     st.session_state['Frequency_of_Traveling_by_Air'],
     st.session_state['Waste_Bag_Size'],
     st.session_state['Energy_efficiency'],
     
     st.session_state['Sex'],
     st.session_state['Heating_Energy_Source'],
     st.session_state['Transport'],
     
     st.session_state['Monthly_Grocery_Bill'],
     st.session_state['Vehicle_Monthly_Distance_Km'],
     st.session_state['Waste_Bag_Weekly_Count'],
     st.session_state['How_Long_TV_PC_Daily_Hour'],
     st.session_state['How_Many_New_Clothes_Monthly'],
     st.session_state['How_Long_Internet_Daily_Hour'],
     st.session_state['Recycling_Metal'],
     st.session_state['Recycling_Glass'],
     st.session_state['Recycling_Paper'],
     st.session_state['Recycling_Plastic'],
     st.session_state['Cooking_With_Stove'],
     st.session_state['Cooking_With_Microwave'],
     st.session_state['Cooking_With_Oven'],
     st.session_state['Cooking_With_Grill']]], columns=all_names)
    
    X = encoder.transform(data)
    #st.write(X)
    #st.write(model.coef_)
    
    prediction = model.predict(X)
    
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(prediction[0])) + " " + unit.translate(SUB))
    #st.write(str(round(prediction[0])))
     
    if st.button("Show How to Improve"):
         st.session_state['prediction'] = prediction[0]
         st.session_state['dataX'] = X
         st.session_state['page'] ='improve'
         st.rerun()
    
def improvement():
    
    X_weighted = np.multiply(st.session_state['dataX'], model.coef_)
    Xsorted = np.sort(X_weighted)
    
    features = encoder.get_feature_names_out()

    n = 7
    topValues = Xsorted[0,(-1*n):]

    topfeatures = []
    for i in topValues:
        ind = np.where(X_weighted[0] == i)
        splitStr = features[ind][0].split('__')
        if splitStr[0] == 'remainder':
            quest = splitStr[1].split('_')[0]
        else:
            quest = splitStr[0]
        topfeatures.append(quest)
        
    ordinalVar=['Body_Type', 'Diet', 'How_Often_Shower', 'Social_Activity', 'Frequency_of_Traveling_by_Air',
                'Waste_Bag_Size', 'Energy_efficiency']
    dummyVar=['Sex', 'Heating_Energy_Source','Transport_Vehicle_Type']
    numVar = ['Monthly_Grocery_Bill','Vehicle_Monthly_Distance_Km', 'Waste_Bag_Weekly_Count', 'How_Long_TV_PC_Daily_Hour',
             'How_Many_New_Clothes_Monthly',  'How_Long_Internet_Daily_Hour']
    restVar = ['Recycling_Glass','Recycling_Metal', 
               'Recycling_Plastic', 'Recycling_Paper',
               'Cooking_With_Oven', 'Cooking_With_Stove', 
               'Cooking_With_Grill','Cooking_With_Microwave']
        
    all_names = ordinalVar + dummyVar + numVar + restVar

    
    st.title("Carbon Footpint Questionnaire")
    
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(st.session_state['prediction'])) + " " + unit.translate(SUB))
    
      
    st.header("How to improve your score:")
 
    if all_names[1] in topfeatures:
        diet_new = st.select_slider("Consider eating less animal products: ", options = ["vegan", "vegetarian", "pescatarian", "omnivore"], value = st.session_state['Diet'])
    else:
        diet_new = st.session_state['Diet']
    if all_names[2] in topfeatures:
        shower_new = st.select_slider("Consider showering less frquently: ", options = ["less frequently", "daily", "more frequently", "twice a day"], value = st.session_state['How_Often_Shower'])
    else:
        shower_new = st.session_state['How_Often_Shower']
    if all_names[3] in topfeatures:
        social_new = st.select_slider("Consider to reduce unnecessary social activiest: ", options = ["never","sometimes", "often"], value = st.session_state['Social_Activity'])
    else:
        social_new = st.session_state['Social_Activity']
    if all_names[4] in topfeatures:
        plane_new = st.select_slider("Consider travelling less by plane: ", options = ["never", "rarely", "frequently", "very frequently"], value = st.session_state['Frequency_of_Traveling_by_Air'])
    else: 
        plane_new = st.session_state['Frequency_of_Traveling_by_Air']
    if all_names[5] in topfeatures:
        wastebag_size_new = st.select_slider("Consider smaller waste bags: ", options = ["small", "medium", "large", "extra large"], value = st.session_state['Waste_Bag_Size'])
    else: 
        wastebag_size_new = st.session_state['Waste_Bag_Size']
    if all_names[6] in topfeatures:
        energy_eff_new = st.select_slider("Consider replacing less efficient appliences: ", options = ["Yes", "Sometimes", "No"], value = st.session_state['Energy_efficiency'])
    else:
        energy_eff_new = st.session_state['Energy_efficiency']
    if all_names[8] in topfeatures:
        heating_new = st.select_slider("Consider switching to a greener energy source: ", options = ["electricity", "wood", "natural gas", "coal"], value = st.session_state['Heating_Energy_Source'])
    else:
        heating_new = st.session_state['Heating_Energy_Source']
    if all_names[9] in topfeatures:
        transport_new = st.select_slider("Consider switching to a better way of transportation: ", 
                                     options = ["car (type: electric)", "car (type: hybrid)","public transport","walk/bicycle", "car (type: diesel)",  "car (type: lpg)", "car (type: petrol)"], value = st.session_state['Transport'])
    else:
          transport_new = st.session_state['Transport']
    if all_names[10] in topfeatures:
        groceries_new = st.slider("Consider buying less groceries: ", 0, st.session_state['Monthly_Grocery_Bill'], st.session_state['Monthly_Grocery_Bill'])
    else:    
        groceries_new = st.session_state['Monthly_Grocery_Bill']
    if all_names[11] in topfeatures:
        km_new = st.slider("Consider to travel less: ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    else:
       km_new = st.session_state['Vehicle_Monthly_Distance_Km']
    if all_names[12] in topfeatures:
        wastebag_count_new = st.slider("Consider prodcing less waste: ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
    else:
        wastebag_count_new = st.session_state['Waste_Bag_Weekly_Count']
    if all_names[13] in topfeatures:
        tvpc_new = st.slider("Consider spending less time infront of the TV/PV: ", 0, st.session_state['How_Long_TV_PC_Daily_Hour'], st.session_state['How_Long_TV_PC_Daily_Hour'])
    else: 
        tvpc_new = st.session_state['How_Long_TV_PC_Daily_Hour']
    if all_names[14] in topfeatures:
        clothes_new = st.slider("Consider buying less new clothes: ", 0, st.session_state['How_Many_New_Clothes_Monthly'], st.session_state['How_Many_New_Clothes_Monthly'])
    else:
        clothes_new = st.session_state['How_Many_New_Clothes_Monthly']
    if all_names[15] in topfeatures:
        internet_new = st.slider("Consider using the internet less: ", 0, st.session_state['How_Long_Internet_Daily_Hour'], st.session_state['How_Long_Internet_Daily_Hour'])
    else:
        internet_new = st.session_state['How_Long_Internet_Daily_Hour']
        
    if not(st.session_state['Recycling_Glass'] == 1 & st.session_state['Recycling_Metal'] == 1 & st.session_state['Recycling_Plastic'] == 1 & st.session_state['Recycling_Paper'] == 1):
        st.write('Have you considered recycling:')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            recycle_new_glass = st.toggle('Glass', value = st.session_state['Recycling_Glass'] == 1)
        with col2:
            recycle_new_metal = st.toggle('Metal', value = st.session_state['Recycling_Metal'] == 1)
        with col3:
            recycle_new_plastic = st.toggle('Plastic', value = st.session_state['Recycling_Plastic'] == 1)
        with col4:
            recycle_new_paper = st.toggle('Paper', value = st.session_state['Recycling_Paper'] == 1)
    else:
        recycle_new_glass = st.session_state['Recycling_Glass']
        recycle_new_metal = st.session_state['Recycling_Metal']
        recycle_new_plastic = st.session_state['Recycling_Plastic']
        recycle_new_paper = st.session_state['Recycling_Paper']
        
    if not((st.session_state['Cooking_With_Oven'] == 0) & (st.session_state['Cooking_With_Stove'] == 0) & (st.session_state['Cooking_With_Grill'] == 0) & (st.session_state['Cooking_With_Microwave'] == 1)):
        st.write('The microwave is the most energy efficient way of cooking')
        microwave_new = st.toggle('Switch to microwave only', value = False)
        if microwave_new:
            cooking_new_oven = 0
            cooking_new_stove = 0
            cooking_new_grill = 0
            cooking_new_microwave = 1
        else:    
            cooking_new_oven = st.session_state['Cooking_With_Oven']
            cooking_new_stove = st.session_state['Cooking_With_Stove']
            cooking_new_grill = st.session_state['Cooking_With_Grill']
            cooking_new_microwave = st.session_state['Cooking_With_Microwave']
    else:    
        cooking_new_oven = st.session_state['Cooking_With_Oven']
        cooking_new_stove = st.session_state['Cooking_With_Stove']
        cooking_new_grill = st.session_state['Cooking_With_Grill']
        cooking_new_microwave = st.session_state['Cooking_With_Microwave']

    data_new = pd.DataFrame([[st.session_state['Body_Type'],
     diet_new,
     shower_new,
     social_new,
     plane_new,
     wastebag_size_new,
     energy_eff_new,
     
     st.session_state['Sex'],
     heating_new,
     transport_new,
     
     groceries_new,
     km_new,
     wastebag_count_new,
     tvpc_new,
     clothes_new,
     internet_new,
     
     recycle_new_glass,
     recycle_new_metal,
     recycle_new_plastic,
     recycle_new_paper,
     cooking_new_oven,
     cooking_new_stove,
     cooking_new_grill,
     cooking_new_microwave]], columns=all_names)
    
    Xnew = encoder.transform(data_new)
    prediction_new = model.predict(Xnew)
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(prediction_new[0])) + " " + unit.translate(SUB))
    
    
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
    elif st.session_state['page'] == 'improve':
        improvement()

if __name__ == '__main__':
 #   st.write("App started")
    main()
    
    