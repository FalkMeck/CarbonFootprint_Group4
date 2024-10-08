# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 13:58:57 2024

@author: falko
"""

import streamlit as st
import pandas as pd
import pickle
import sklearn
import numpy as np
import matplotlib.image as img
import math
import plotly.express as px
import lightgbm as lgb
from PIL import Image
from fastai.callback.progress import ProgressCallback
from fastai.vision.all import *


# st.write(sklearn.__version__)

st.set_page_config(
    page_title="Carbon Footprint",
    page_icon="👣")

## Create the survey
#LOCAL
# Function to load model and encoder, cached using st.cache_resource
@st.cache_resource
def load_model_and_encoder():
    with open('model2.pkl', 'rb') as f:
        model_f = pickle.load(f)
    with open('encoder2.pkl', 'rb') as f:
        encoder_f = pickle.load(f)
    with open('CFdata.pkl', 'rb') as f:
        CFdata_f = pickle.load(f)
    return model_f, encoder_f, CFdata_f

@st.cache_resource
def load_model_tree():
    with open('tree.pkl', 'rb') as f:
        model_f = pickle.load(f)
    return model_f

@st.cache_resource
def load_model_and_encoder_lgbm():
    with open('model_s.pkl', 'rb') as f:
        model_f = pickle.load(f)
    with open('encoder_s.pkl', 'rb') as f:
        encoder_f = pickle.load(f)

    return model_f, encoder_f

@st.cache_resource
def load_earth_image():
    image = img.imread('earth.jpg') 
    return image


@st.cache_resource
def load_image_classifier():
    with open('model_image-classifier.pkl', 'rb') as f:
       learner_f= load_learner(f)
    return learner_f

def predict_image(img, learner):
    # Disable callbacks (including progress bar) during prediction
    with learner.no_bar():
        pred_class, pred_idx, probs = learner.predict(img)
    return pred_class, probs[pred_idx]

model_reg,encoder,cfdata = load_model_and_encoder()
model_dt = load_model_tree()
model_lgbm, encoder_lgbm = load_model_and_encoder_lgbm()
learner = load_image_classifier()
earth = load_earth_image()


# # Declare the custom component to get the width of the image container
# get_width = st.components.v1.declare_component(
#     "get_width",
#     path="."  # Assume you have a local custom component for simplicity
# )

# # Custom JavaScript to find the width of the container
# container_width_js = """
#     <script>
#     const imageContainer = document.querySelector(".element-container");
#     const containerWidth = imageContainer.offsetWidth;
#     Streamlit.setComponentValue(containerWidth);
#     </script>
# """

def reg_survey_welcome():
    st.title("Carbon Footprint Questionnaire")

    st.write("""
             Hello you there, 
             
             this questionnaire helps you to figure out,
             what your current, monthly Carbon Footprint is.
             
             After that it will show you your main areas of concern.
             You can play around with how improving in these areas would reduce your Carbon Footprint.
             
             Thank you for caring for the environment!
             """)
    
    if st.button("Start"):
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def reg_survey_demo():
    st.title("Carbon Footprint Questionnaire")
    st.header("Demographics")
    st.write("First, we start with some inforamtion about yourself...")
    
    # QUESTION FOR HEIGHT
    if 'Height_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Height_tmp'] # use previous value
    else:
        default = 170 # use default
    height = st.number_input("Height (in cm):", min_value = 50, max_value = 270, value = default)
    
    # QUESION FOR WEIGHT
    if 'Weight_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Weight_tmp'] # use previous answer
    else:
        default = 70 # use default
    weight = st.number_input("Weight (in kg):", min_value = 30, max_value = 600, value = default)
    
    # QUESTION FOR SEX
    questOptions = ["female", "male"] # define options
    if 'Sex' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Sex']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    sex = st.radio("Sex:", options = questOptions, horizontal = True, index = default)
    
    # QUESTION FOR Diet
    questOptions = ["omnivore", "pescatarian", "vegetarian", "vegan"] # define options
    if 'Diet' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Diet']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    diet = st.radio("What is your diet?", options = questOptions, horizontal = True, index = default)

    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    
    if Next:
        
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
        st.session_state['Height_tmp'] = height
        st.session_state['Weight_tmp'] = weight
        st.session_state['Sex'] = sex
        st.session_state['Diet'] = diet
        st.session_state['page'] = 'survey_life'
        st.rerun()        

def reg_survey_life():
    st.title("Carbon Footprint Questionnaire")
    st.header("Daily life")
    st.write("Now some questions about your day to day activties, expenses and the waste you produce.")
    
    # QUESTION FOR Showering
    questOptions = ["less frequently", "daily", "twice a day", "more frequently"] # define options
    if 'How_Often_Shower' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['How_Often_Shower']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    shower = st.radio("How often do you shower?", options = questOptions, horizontal = True, index = default)
    
    # QUESTION FOR Social activities
    questOptions = ["never","sometimes", "often"] # define options
    if 'Social_Activity' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Social_Activity']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    social = st.radio("How often do you engage in social activities?", options = questOptions, horizontal = True, index = default)
    
    # QUESTION FOR Groceries
    if 'Monthly_Grocery_Bill' in st.session_state: # check if previously answered
        default = int(st.session_state['Monthly_Grocery_Bill']/1.1) # use previous value
    else:
        default = int(173/1.1) # use default
    groceries = st.number_input("How much do you spend on groceries in a month (in Euro)?", min_value = 0, max_value = int(1e6), value = default)
    
    # QUESTION FOR New CLothes
    if 'How_Many_New_Clothes_Monthly' in st.session_state: # check if previously answered
        default = st.session_state['How_Many_New_Clothes_Monthly'] # use previous value
    else:
        default = 1 # use default
    clothes = st.number_input("How many new pieces of clothing do you buy in a month?", min_value = 0, max_value = int(1e6), value = default)    
    
    # QUESTION FOR Waste Bag size
    questOptions = ["small", "medium", "large", "extra large"] # define options
    if 'Waste_Bag_Size' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Waste_Bag_Size']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    wastebag_size = st.radio("Which size of trashbag are you using?", options = questOptions, horizontal = True, index = default)
    
    # QUESTION FOR Waste Bag Count
    if 'Waste_Bag_Weekly_Count' in st.session_state: # check if previously answered
        default = st.session_state['Waste_Bag_Weekly_Count'] # use previous value
    else:
        default = 4 # use default
    wastebag_count = st.number_input("How many bags of waste do you produce per week?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR RECYCLING
    recycle_options = ["Paper", "Plastic", "Glass","Metal"]
    default = []
    if 'Recycling_Paper' in st.session_state:
        for rec in recycle_options:
            if st.session_state['Recycling_' + rec] == 1:
                default.append(rec)
    recycle = st.multiselect("Which of the following materials are you recycling?", options = recycle_options, default = default)
    
    # QUESTION FOR TV/PC usage
    if 'How_Long_TV_PC_Daily_Hour' in st.session_state: # check if previously answered
        default = st.session_state['How_Long_TV_PC_Daily_Hour'] # use previous value
    else:
        default = 12 # use default
    tvpc = st.number_input("How many hours do you spend infront of the TV or PC per day?", min_value = 0, max_value = 24, value = default)
    
    # QUESTION FOR Internet usage
    if 'How_Long_Internet_Daily_Hour' in st.session_state: # check if previously answered
        default = st.session_state['How_Long_Internet_Daily_Hour'] # use previous value
    else:
        default = 12 # use default
    internet = st.number_input("How many hours do you use the internet per day?", min_value = 0, max_value = 24, value = default)
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    with col1:
       Back = st.button("Back")
    
    if Next or Back:
        st.session_state['How_Often_Shower'] = shower
        st.session_state['Social_Activity'] = social
        st.session_state['Monthly_Grocery_Bill'] = groceries*1.1
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Waste_Bag_Size'] = wastebag_size
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        for rec in recycle_options:
            st.session_state['Recycling_' + rec] = 1 if rec in recycle else 0
        st.session_state['How_Long_TV_PC_Daily_Hour'] = tvpc
        st.session_state['How_Long_Internet_Daily_Hour'] = internet
    
    if Next:
        st.session_state['page'] = 'survey_energy'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def reg_survey_energy():
    st.title("Carbon Footprint Questionnaire")
    st.header("Energy efficiency")
    st.write("How enegery efficient are you already?")
    
    # QUESTION FOR Energy of you heating source
    questOptions = ["coal", "electricity", "natural gas", "wood"] # define options
    if 'Heating_Energy_Source' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Heating_Energy_Source']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    energy = st.radio("What is your main source of engery for heating?", options = questOptions, horizontal = True, index = default)
    
    # QUESTION FOR your cooking appliences
    cooking_options = ["Stove", "Oven", "Microwave", "Grill"]
    default = []
    if 'Cooking_With_Stove' in st.session_state:
        for cook in cooking_options:
            if st.session_state['Cooking_With_' + cook] == 1:
                default.append(cook)
    cooking = st.multiselect("Which of the following appliances do you use for cooking?", options = cooking_options, default = default)
    
    # QUESTION FOR Energy efficiency
    questOptions = ["Yes", "Sometimes", "No"] # define options
    if 'Energy_efficiency' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Energy_efficiency']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    energy_eff = st.radio("Would you consider your electric appliances as energy efficient?", options = questOptions, horizontal = True, index = default)
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    with col1:
       Back = st.button("Back")

    if Next or Back:
        st.session_state['Heating_Energy_Source'] = energy
        for cook in cooking_options:
            st.session_state['Cooking_With_' + cook] = 1 if cook in cooking else 0
        st.session_state['Energy_efficiency'] = energy_eff
    if Next:
        st.session_state['page'] ='survey_travel'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_life'
        st.rerun()           

def reg_survey_travel():
    st.title("Carbon Footprint Questionnaire")
    st.header("Travelling")
    st.write("Lastly, some question about yout means of getting around and how much you travel.")
    
    # QUESTION FOR main means of transportations
    questOptions = ["walk/bicycle", "public transport", "car (type: petrol)", "car (type: diesel)", "car (type: electric)", "car (type: hybrid)", "car (type: lpg)"]# define options
    if 'Transport' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Transport']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    transport = st.radio("What is your main method of transportation?", options = questOptions, horizontal = False, index = default)
   
    # QUESTION FOR distance traveled monthly
    if 'Vehicle_Monthly_Distance_Km' in st.session_state: # check if previously answered
        default = st.session_state['Vehicle_Monthly_Distance_Km'] # use previous value
    else:
        default = 823 # use default
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Frequency of plane usage
    questOptions = ["never", "rarely", "frequently", "very frequently"] # define options
    if 'Frequency_of_Traveling_by_Air' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Frequency_of_Traveling_by_Air']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    plane = st.radio("How often did you travel by plane in the last month?", options = questOptions, horizontal = True, index = default)

    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Show Results")
    with col1:
       Back = st.button("Back")

    if Next or Back:
         st.session_state['Transport'] = transport
         st.session_state['Vehicle_Monthly_Distance_Km'] = km
         st.session_state['Frequency_of_Traveling_by_Air'] = plane
    if Next:
         st.session_state['page'] ='results'
         st.rerun()
    if Back:
         st.session_state['page'] = 'survey_energy'
         st.rerun()

def reg_results():
    st.title("Carbon Footprint Questionnaire")
    st.header("Results")

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
     st.session_state['Recycling_Glass'],
     st.session_state['Recycling_Metal'],
     st.session_state['Recycling_Plastic'],
     st.session_state['Recycling_Paper'],
     st.session_state['Cooking_With_Oven'],
     st.session_state['Cooking_With_Stove'],
     st.session_state['Cooking_With_Grill'],
     st.session_state['Cooking_With_Microwave']]], columns=all_names)
    
    X = encoder.transform(data)
    #st.write(X)
    #st.write(model.coef_)
    
    prediction = model_reg.predict(X)
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    predValue = max([0,prediction[0]])
    st.header(str(round(predValue)) + " " + unit.translate(SUB))
    #st.write(str(round(prediction[0])))
    
    st.write("This is where that leaves you in comparision to the population:")
    fig = px.histogram(cfdata, nbins=100, title='Interactive Histogram of Carbon Emissions', marginal='rug')
    fig.update_layout(
        xaxis_title='Carbon Emissions (' + unit.translate(SUB)+ ')',
        yaxis_title='Frequency',
        bargap=0,
        template='plotly_dark',
        showlegend=False
        )
    fig.add_vline(x=predValue, line_width=3, line_dash="solid", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    
    sequestration_rate = 2100
    gha_earth = 1.63

    earths = round(((predValue*12)/sequestration_rate)/gha_earth,3)
    earths_max = math.ceil(earths)
    
    earthsImage = []
    for i in range(earths_max):
        if i == 0:
            earthsImage = earth
        else:
            earthsImage = np.append(earthsImage, earth, 1)
        
    st.write("You woud need")
    st.header(str(earths) + " Earths to live")
    
    # Render the JS and get the width
  #  colWidth = get_width(html=container_width_js)
   # earth_width = min(colWidth , int(earths*earth.shape[1]*0.1))
    if earths_max > 0:
        st.image(earthsImage[:,range(int(earths*earth.shape[1])),:], channels="RGB", output_format="auto",width = None)
     
    
    if st.button("Show How to Improve"):
         st.session_state['prediction'] = predValue
         st.session_state['dataX'] = X
         st.session_state['page'] ='improve'
         st.rerun()
    
def reg_improvement():
    
    X_weighted = np.multiply(st.session_state['dataX'], model_reg.coef_)
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

    
    st.title("Carbon Footprint Questionnaire")
    
    st.write("Your current, monthly Carbon Footprint before applying any changes is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(st.session_state['prediction'])) + " " + unit.translate(SUB))
    
      
    st.header("How to improve your score:")
 
    if all_names[1] in topfeatures:
        diet_new = st.select_slider("Consider eating less animal products: ", options = ["vegan", "vegetarian", "pescatarian", "omnivore"], value = st.session_state['Diet'])
    else:
        diet_new = st.session_state['Diet']
    if all_names[2] in topfeatures:
        shower_new = st.select_slider("Consider showering less frequently: ", options = ["less frequently", "daily", "twice a day", "more frequently"], value = st.session_state['How_Often_Shower'])
    else:
        shower_new = st.session_state['How_Often_Shower']
    if all_names[3] in topfeatures:
        social_new = st.select_slider("Consider to reduce unnecessary social activities: ", options = ["never","sometimes", "often"], value = st.session_state['Social_Activity'])
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
        transportOptions = ["car (type: electric)", "car (type: hybrid)","public transport","walk/bicycle", "car (type: diesel)",  "car (type: lpg)", "car (type: petrol)"]
        transIndex = transportOptions.index(st.session_state['Transport'])
        transport_new = st.selectbox("Consider switching to a environmentally more friendly way of transportation: ", options = transportOptions, index = transIndex)
    else:
          transport_new = st.session_state['Transport']
    if all_names[10] in topfeatures:
        groceries_new = st.slider("Consider spending less on groceries (in Euro): ", 0.0, st.session_state['Monthly_Grocery_Bill']/1.1, st.session_state['Monthly_Grocery_Bill']/1.1)*1.1
    else:    
        groceries_new = st.session_state['Monthly_Grocery_Bill']
    if all_names[11] in topfeatures:
        km_new = st.slider("Consider travelling less (in km): ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    else:
       km_new = st.session_state['Vehicle_Monthly_Distance_Km']
    if all_names[12] in topfeatures:
        wastebag_count_new = st.slider("Consider producing less waste (less bags of waste): ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
    else:
        wastebag_count_new = st.session_state['Waste_Bag_Weekly_Count']
    if all_names[13] in topfeatures:
        tvpc_new = st.slider("Consider spending less hours infront of the TV/PV: ", 0, st.session_state['How_Long_TV_PC_Daily_Hour'], st.session_state['How_Long_TV_PC_Daily_Hour'])
    else: 
        tvpc_new = st.session_state['How_Long_TV_PC_Daily_Hour']
    if all_names[14] in topfeatures:
        clothes_new = st.slider("Consider buying less new clothes: ", 0, st.session_state['How_Many_New_Clothes_Monthly'], st.session_state['How_Many_New_Clothes_Monthly'])
    else:
        clothes_new = st.session_state['How_Many_New_Clothes_Monthly']
    if all_names[15] in topfeatures:
        internet_new = st.slider("Consider spending less hours on the internet: ", 0, st.session_state['How_Long_Internet_Daily_Hour'], st.session_state['How_Long_Internet_Daily_Hour'])
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
    prediction_new = model_reg.predict(Xnew)
    st.write("If you would apply these change, your new, monthly Carbon Footprint would be:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue_new = max([0,prediction_new[0]])
    st.header(str(round(predValue_new)) + " " + unit.translate(SUB))
    
    st.write("That is an improvement of " + str(round(st.session_state['prediction']) - round(predValue_new)) + " " + unit.translate(SUB)+" per month!")
    
    fig = px.histogram(cfdata, nbins=100, title='Interactive Histogram of Carbon Emissions', marginal='rug')
    fig.update_layout(
        xaxis_title='Carbon Emissions (' + unit.translate(SUB)+ ')',
        yaxis_title='Frequency',
        bargap=0,
        template='plotly_dark',
        showlegend=False
        )
    fig.add_vline(x=predValue_new, line_width=3, line_dash="solid", line_color="green")
    fig.add_vline(x=st.session_state['prediction'], line_width=3, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)


def short_survey_welcome():
    st.title("Carbon Footprint Questionnaire")

    st.write("""
             Hello you there, 
             
             this questionnaire helps you to figure out,
             what your current, monthly Carbon Footprint is.
             
             After that it will show you your main areas of concern.
             You can play around with how improving in these areas would reduce your Carbon Footprint.
             
             Thank you for caring for the environment!
             """)
    
    if st.button("Start"):
        st.session_state['page'] = 'image_class'
        st.rerun() 
    
    

def short_survey_image_classifier():
    st.title("Carbon Footprint Questionnaire")
    st.header("Mode of Transportation")
    
    st.write("Please upload a picture of your usual mode of transport?")
    prob = None;
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"], accept_multiple_files=False)
    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert('RGB')
       
        st.image(img, caption = 'Uploaded image', use_column_width= True)
        st.write("")
        
        st.write("Classifying...")
        this_is, prob = predict_image(img, learner)
        st.write(f"Prediction: {this_is}, Confidence: {prob}")
        st.write(f"This is a: {this_is}.")
    if prob is not None:
        if prob <= 0.95:
            st.write("Sorry, the image classification was not successful. Please select your mode of transportation manually.")
            questOptions = ["walk/bicycle", "public", "petrol", "diesel", "electric", "hybrid", "lpg"]# define options
            if 'Transport' in st.session_state: # check if question has been nswered yet
                default = questOptions.index(st.session_state['Transport']) # use previous index of answer
            else:
                default = 0 # default is using first answer
            transport = st.radio("What is your main method of transportation?", options = questOptions, horizontal = False, index = default)
        else:
            if this_is == 'car':
                questOptions = ["petrol", "diesel", "electric", "hybrid", "lpg"]# define options
                if 'Transport' in st.session_state and st.session_state['Transport'] in questOptions: # check if question has been nswered yet
                    default = questOptions.index(st.session_state['Transport']) # use previous index of answer
                else:
                    default = 0 # default is using first answer
                transport = st.radio("Please select the fuel source of your car.", options = questOptions, horizontal = False, index = default)
            else: 
                if this_is == 'bus':
                    transport = "public"
                elif this_is == 'bicycle':
                    transport ="walk/bicycle"
            
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    
    if Next:

        st.session_state['Transport'] = transport        
        st.session_state['page'] = 'Rest_quests'
        st.rerun()    


   
                
def short_survey_rest():
    st.title("Carbon Footprint Questionnaire")
    st.header("Remaining Questions")
    st.write("Please answer the remaining 6 questions.")
    
    
    # QUESTION FOR HEIGHT
    if 'Height_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Height_tmp'] # use previous value
    else:
        default = 170 # use default
    height = st.number_input("Height (in cm):", min_value = 50, max_value = 270, value = default)
    
    # QUESION FOR WEIGHT
    if 'Weight_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Weight_tmp'] # use previous answer
    else:
        default = 70 # use default
    weight = st.number_input("Weight (in kg):", min_value = 30, max_value = 600, value = default)
    
    # QUESTION FOR New CLothes
    if 'How_Many_New_Clothes_Monthly' in st.session_state: # check if previously answered
        default = st.session_state['How_Many_New_Clothes_Monthly'] # use previous value
    else:
        default = 1 # use default
    clothes = st.number_input("How many new pieces of clothing do you buy in a month?", min_value = 0, max_value = int(1e6), value = default)    
    
    # QUESTION FOR Waste Bag Count
    if 'Waste_Bag_Weekly_Count' in st.session_state: # check if previously answered
        default = st.session_state['Waste_Bag_Weekly_Count'] # use previous value
    else:
        default = 4 # use default
    wastebag_count = st.number_input("How many bags of waste do you produce per week?", min_value = 0, max_value = int(1e6), value = default)
    
    # QUESTION FOR distance traveled monthly
    if 'Vehicle_Monthly_Distance_Km' in st.session_state: # check if previously answered
        default = st.session_state['Vehicle_Monthly_Distance_Km'] # use previous value
    else:
        default = 823 # use default
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Frequency of plane usage
    questOptions = ["never", "rarely", "frequently", "very frequently"] # define options
    if 'Frequency_of_Traveling_by_Air' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Frequency_of_Traveling_by_Air']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    plane = st.radio("How often did you travel by plane in the last month?", options = questOptions, horizontal = True, index = default)

    
  
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Show Results")
    with col1:
       Back = st.button("Back")       
    
    if Next or Back:
         
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Vehicle_Monthly_Distance_Km'] = km
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        st.session_state['Frequency_of_Traveling_by_Air'] = plane
            
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
       
        
        st.session_state['Height_tmp'] = height
        st.session_state['Weight_tmp'] = weight
        
    if Next:
        st.session_state['page'] = 'results'
        st.rerun()    
    
    if Back:
      st.session_state['page'] = 'image_class'
      st.rerun()     
            


def lgbm_survey_welcome():
    st.title("Carbon Footprint Questionnaire")

    st.write("""
             Hello you there, 
             
             this questionnaire helps you to figure out,
             what your current, monthly Carbon Footprint is.
             
             After that it will show you your main areas of concern.
             You can play around with how improving in these areas would reduce your Carbon Footprint.
             
             Thank you for caring for the environment!
             """)
    
    if st.button("Start"):
        st.session_state['page'] = 'survey_all'
        st.rerun()

def lgbm_survey_all():
    st.title("Carbon Footprint Questionnaire")
    st.header("7 Questions")
    st.write("This short version of the questionnaire, only has 7 questions.")
    
    
    # QUESTION FOR HEIGHT
    if 'Height_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Height_tmp'] # use previous value
    else:
        default = 170 # use default
    height = st.number_input("Height (in cm):", min_value = 50, max_value = 270, value = default)
    
    # QUESION FOR WEIGHT
    if 'Weight_tmp' in st.session_state: # check if previously answered
        default = st.session_state['Weight_tmp'] # use previous answer
    else:
        default = 70 # use default
    weight = st.number_input("Weight (in kg):", min_value = 30, max_value = 600, value = default)
    
    # QUESTION FOR New CLothes
    if 'How_Many_New_Clothes_Monthly' in st.session_state: # check if previously answered
        default = st.session_state['How_Many_New_Clothes_Monthly'] # use previous value
    else:
        default = 1 # use default
    clothes = st.number_input("How many new pieces of clothing do you buy in a month?", min_value = 0, max_value = int(1e6), value = default)    
    
    # QUESTION FOR Waste Bag Count
    if 'Waste_Bag_Weekly_Count' in st.session_state: # check if previously answered
        default = st.session_state['Waste_Bag_Weekly_Count'] # use previous value
    else:
        default = 4 # use default
    wastebag_count = st.number_input("How many bags of waste do you produce per week?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR main means of transportations
    questOptions = ["walk/bicycle", "public", "petrol", "diesel", "electric", "hybrid", "lpg"]# define options
    if 'Transport' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Transport']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    transport = st.radio("What is your main method of transportation?", options = questOptions, horizontal = False, index = default)
   
    # QUESTION FOR distance traveled monthly
    if 'Vehicle_Monthly_Distance_Km' in st.session_state: # check if previously answered
        default = st.session_state['Vehicle_Monthly_Distance_Km'] # use previous value
    else:
        default = 823 # use default
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Frequency of plane usage
    questOptions = ["never", "rarely", "frequently", "very frequently"] # define options
    if 'Frequency_of_Traveling_by_Air' in st.session_state: # check if question has been nswered yet
        default = questOptions.index(st.session_state['Frequency_of_Traveling_by_Air']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    plane = st.radio("How often did you travel by plane in the last month?", options = questOptions, horizontal = True, index = default)

    
  
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Show Results")
    
    if Next:
        
         
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Vehicle_Monthly_Distance_Km'] = km
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        st.session_state['Transport'] = transport
        st.session_state['Frequency_of_Traveling_by_Air'] = plane
            
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
       
        
        st.session_state['Height_tmp'] = height
        st.session_state['Weight_tmp'] = weight
        
        st.session_state['page'] = 'results'
        st.rerun()    
            
            
            
            
def lgbm_results():
    st.title("Carbon Footprint Questionnaire")
    st.header("Results")
    
    all_names = ['Vehicle_Monthly_Distance_Km',
                 'How_Many_New_Clothes_Monthly',
                 'Waste_Bag_Weekly_Count',
                 'Frequency_of_Traveling_by_Air',
                 'Body_Type',
                 'Transport_Vehicle_Type']
    
    data = pd.DataFrame([[st.session_state['Vehicle_Monthly_Distance_Km'],
                         st.session_state['How_Many_New_Clothes_Monthly'],
                         st.session_state['Waste_Bag_Weekly_Count'],
                         st.session_state['Frequency_of_Traveling_by_Air'],
                         st.session_state['Body_Type'],
                         st.session_state['Transport']]], columns=all_names)
    
    X = encoder_lgbm.transform(data)

    prediction = model_lgbm.predict(X)
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue = max([0,prediction[0]])
    st.header(str(round(predValue)) + " " + unit.translate(SUB))
    
    st.write("This is where that leaves you in comparision to the population:")
    fig = px.histogram(cfdata, nbins=100, title='Interactive Histogram of Carbon Emissions', marginal='rug')
    fig.update_layout(
        xaxis_title='Carbon Emissions (' + unit.translate(SUB)+ ')',
        yaxis_title='Frequency',
        bargap=0,
        template='plotly_dark',
        showlegend=False
        )
    fig.add_vline(x=predValue, line_width=3, line_dash="solid", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    
    sequestration_rate = 2100
    gha_earth = 1.63

    earths = round(((predValue*12)/sequestration_rate)/gha_earth,3)
    earths_max = math.ceil(earths)

    earthsImage = []
    for i in range(earths_max):
        if i == 0:
            earthsImage = earth
        else:
            earthsImage = np.append(earthsImage, earth, 1)
    
    st.write("You woud need")
    st.header(str(earths) + " Earths to live")
    
   # colWidth = get_width(html=container_width_js)
  #  earth_width = min(colWidth , int(earths*earth.shape[1]*0.1))
   # st.write(colWidth)
    if earths_max > 0:
        st.image(earthsImage[:,range(int(earths*earth.shape[1])),:], channels="RGB", output_format="auto",width = None)
    
    
    if st.button("Show How to Improve"):
         st.session_state['prediction'] = predValue
         st.session_state['page'] ='improve'
         st.rerun()
    
def lgbm_improvement():
    
        
    all_names = ['Vehicle_Monthly_Distance_Km',
                 'How_Many_New_Clothes_Monthly',
                 'Waste_Bag_Weekly_Count',
                 'Frequency_of_Traveling_by_Air',
                 'Body_Type',
                 'Transport_Vehicle_Type']
    
    st.title("Carbon Footprint Questionnaire")
    
    st.write("Your current, monthly Carbon Footprint before applying any changes is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(st.session_state['prediction'])) + " " + unit.translate(SUB))

    st.header("How to improve your score:")
 
    plane_new = st.select_slider("Consider travelling less by plane: ", options = ["never", "rarely", "frequently", "very frequently"], value = st.session_state['Frequency_of_Traveling_by_Air'])
    
    transportOptions = ["electric", "hybrid", "public" ,"walk/bicycle", "diesel", "lpg", "petrol"]
    transIndex = transportOptions.index(st.session_state['Transport'])
    transport_new = st.selectbox("Consider switching to a environmentally more friendly way of transportation: ", options = transportOptions, index = transIndex)
     
    km_new = st.slider("Consider travelling less (in km): ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    
    wastebag_count_new = st.slider("Consider producing less waste (less bags of waste): ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
    
    clothes_new = st.slider("Consider buying less new clothes: ", 0, st.session_state['How_Many_New_Clothes_Monthly'], st.session_state['How_Many_New_Clothes_Monthly'])
    
    data_new = pd.DataFrame([[km_new,
                              clothes_new,
                              wastebag_count_new,
                              plane_new,
                              st.session_state['Body_Type'],
                              transport_new]], columns=all_names)
    X_new = encoder_lgbm.transform(data_new)
    prediction_new = model_lgbm.predict(X_new)
    st.write("If you would apply these change, your new, monthly Carbon Footprint would be:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue_new = max([0,prediction_new[0]])
    st.header(str(round(predValue_new)) + " " + unit.translate(SUB))
    
    st.write("That is an improvement of " + str(round(st.session_state['prediction']) - round(predValue_new)) + " " + unit.translate(SUB)+" per month!")
    
    fig = px.histogram(cfdata, nbins=100, title='Interactive Histogram of Carbon Emissions', marginal='rug')
    fig.update_layout(
        xaxis_title='Carbon Emissions (' + unit.translate(SUB)+ ')',
        yaxis_title='Frequency',
        bargap=0,
        template='plotly_dark',
        showlegend=False
        )
    fig.add_vline(x=predValue_new, line_width=3, line_dash="solid", line_color="green")
    fig.add_vline(x=st.session_state['prediction'], line_width=3, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    
def selction_tool():
    st.header("Please select the Version of the App you would like to do:")
    with open("test.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
      Regression = st.button("Questionnaire \n (3 min)")
    with col2:
        RegShort = st.button("Questionnaire \n (1 min)")
    with col3:
       RegShortPlus = st.button("Questionnaire \n (with Image Classification)")
    with col4:
        st.download_button(label="Download Decision Tree Print-Out", data=PDFbyte, file_name="test.pdf", mime='application/octet-stream')
        
       
    if Regression:
        st.session_state['model'] = 'regression'
        st.session_state['page'] = 'survey_welcome'
    elif RegShort:
        st.session_state['model'] = 'regShort'
        st.session_state['page'] = 'survey_welcome'
    elif RegShortPlus:
         st.session_state['model'] = 'regShort_plus'
         st.session_state['page'] = 'survey_welcome' 
        
        
def main():
    
        if 'page' not in st.session_state:
            st.session_state['page'] = 'decision_page'  
            
        if st.session_state['page'] == 'decision_page':
            if 'model' not in st.session_state:
                st.session_state['model'] = 'MT'
            selction_tool()
            
        if st.session_state['model'] == 'regression' and st.session_state['page'] == 'survey_welcome':
            reg_survey_welcome()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'survey_demo':
            reg_survey_demo()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'survey_life':
            reg_survey_life()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'survey_energy':
            reg_survey_energy()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'survey_travel':
            reg_survey_travel()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'results':
            reg_results()
        elif st.session_state['model'] == 'regression' and st.session_state['page'] == 'improve':
            reg_improvement()
         
        elif st.session_state['model'] == 'regShort' and st.session_state['page'] == 'survey_welcome':
            lgbm_survey_welcome()
        elif st.session_state['model'] == 'regShort' and st.session_state['page'] == 'survey_all':
            lgbm_survey_all()
        elif st.session_state['model'] == 'regShort' and st.session_state['page'] == 'results':
            lgbm_results()
        elif st.session_state['model'] == 'regShort' and st.session_state['page'] == 'improve':
            lgbm_improvement()    
         
        elif st.session_state['model'] == 'regShort_plus' and st.session_state['page'] == 'survey_welcome':
            short_survey_welcome()
        elif st.session_state['model'] == 'regShort_plus' and st.session_state['page'] == 'image_class':
            short_survey_image_classifier()
        elif st.session_state['model'] == 'regShort_plus' and st.session_state['page'] == 'Rest_quests':
            short_survey_rest()
        elif st.session_state['model'] == 'regShort_plus' and st.session_state['page'] == 'results':
            lgbm_results()
        elif st.session_state['model'] == 'regShort_plus' and st.session_state['page'] == 'improve':
            lgbm_improvement()

if __name__ == '__main__':
 #  st.write("App started")
   main()