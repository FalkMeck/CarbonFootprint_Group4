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
def load_model_lgbm():
    with open('lgbm.pkl', 'rb') as f:
        model_f = pickle.load(f)

    return model_f

@st.cache_resource
def load_earth_image():
    image = img.imread('earth.jpg') 
    return image

model_reg,encoder,cfdata = load_model_and_encoder()
model_dt = load_model_tree()
model_lgbm = load_model_lgbm()
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
    st.title("Carbon Footpint Questionnaire")
    st.header("Daily life")
    st.write("Now some questions about your day to day activties, expenses and the waste you produce.")
    
    # QUESTION FOR Showering
    questOptions = ["daily", "less frequently", "twice a day", "more frequently"] # define options
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
        default = st.session_state['Monthly_Grocery_Bill'] # use previous value
    else:
        default = 1 # use default
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
        default = 1 # use default
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
        default = 1 # use default
    tvpc = st.number_input("How many hours do you spend infront of the TV or PC per day?", min_value = 0, max_value = 24, value = default)
    
    # QUESTION FOR Internet usage
    if 'How_Long_Internet_Daily_Hour' in st.session_state: # check if previously answered
        default = st.session_state['How_Long_Internet_Daily_Hour'] # use previous value
    else:
        default = 1 # use default
    internet = st.number_input("How many hours do you use the internet per day?", min_value = 0, max_value = 24, value = default)
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    with col1:
       Back = st.button("Back")
    
    if Next:
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
        
        st.session_state['page'] = 'survey_energy'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def reg_survey_energy():
    st.title("Carbon Footpint Questionnaire")
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

    if Next:
        st.session_state['Heating_Energy_Source'] = energy
        for cook in cooking_options:
            st.session_state['Cooking_With_' + cook] = 1 if cook in cooking else 0
        st.session_state['Energy_efficiency'] = energy_eff
        
        st.session_state['page'] ='survey_travel'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_life'
        st.rerun()           

def reg_survey_travel():
    st.title("Carbon Footpint Questionnaire")
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
        default = 1 # use default
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

    if Next:
         st.session_state['Transport'] = transport
         st.session_state['Vehicle_Monthly_Distance_Km'] = km
         st.session_state['Frequency_of_Traveling_by_Air'] = plane
         
         st.session_state['page'] ='results'
         st.rerun()
    if Back:
         st.session_state['page'] = 'survey_energy'
         st.rerun()

def reg_results():
    st.title("Carbon Footpint Questionnaire")
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
    predValue = max(prediction[0],0)
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

    
    st.title("Carbon Footpint Questionnaire")
    
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
        shower_new = st.select_slider("Consider showering less frquently: ", options = ["less frequently", "daily", "twice a day", "more frequently"], value = st.session_state['How_Often_Shower'])
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
        transport_new = st.selectbox("Consider switching to a better way of transportation: ", options = transportOptions, index = transIndex)
    else:
          transport_new = st.session_state['Transport']
    if all_names[10] in topfeatures:
        groceries_new = st.slider("Consider buying less groceries: ", 0, st.session_state['Monthly_Grocery_Bill']/1.1, st.session_state['Monthly_Grocery_Bill']/1.1)*1.1
    else:    
        groceries_new = st.session_state['Monthly_Grocery_Bill']
    if all_names[11] in topfeatures:
        km_new = st.slider("Consider to travel less: ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    else:
       km_new = st.session_state['Vehicle_Monthly_Distance_Km']
    if all_names[12] in topfeatures:
        wastebag_count_new = st.slider("Consider producing less waste: ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
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
    prediction_new = model_reg.predict(Xnew)
    st.write("If you would apply these change, your new, monthly Carbon Footprint would be:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue_new = max(prediction_new[0],0)
    st.write(predValue_new)
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

def dt_survey_welcome():
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

def dt_survey_demo():
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
    questOptions = ["male", "female"] # define options
    if 'Sex' in st.session_state: # check if question has been nswered yet
        default = st.session_state['Sex'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    sex = st.radio("Sex:", options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)
    
    # QUESTION FOR Diet
    questOptions = ["vegan", "vegetarian", "pescatarian", "omnivore"] # define options
    if 'Diet' in st.session_state: # check if question has been nswered yet
        default = st.session_state['Diet'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    diet = st.radio("What is your diet?", options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)

    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    
    if Next:
        
        bmi = weight/((height/100)**2)
    
        body_type = "";
        if bmi >= 30 :
            body_type = 3
        elif bmi >= 25:
            body_type = 2
        elif bmi >= 18.5:
            body_type = 1
        else:
            body_type = 0
        st.session_state['Body_Type'] = body_type
        st.session_state['Height_tmp'] = height
        st.session_state['Weight_tmp'] = weight
        st.session_state['Sex'] = sex
        st.session_state['Diet'] = diet
        st.session_state['page'] = 'survey_life'
        st.rerun()    

def dt_survey_life():
    st.title("Carbon Footpint Questionnaire")
    st.header("Daily life")
    
    
    st.write("Now some questions about your day to day activties, expenses and the waste you produce.")
    
    # QUESTION FOR Showering
    questOptions = ["less than daily", "daily", "twice a day", "more frequently"] # define options
    if 'How_Often_Shower' in st.session_state: # check if question has been nswered yet
        default = st.session_state['How_Often_Shower'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    shower = st.radio("How often do you shower?", options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)
    
    # QUESTION FOR Social activities
    questOptions = ["never","sometimes", "often"] # define options
    if 'Social_Activity' in st.session_state: # check if question has been nswered yet
        default = st.session_state['Social_Activity'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    social = st.radio("How often do you engage in social activities?",  options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)
    
    # QUESTION FOR Groceries
    if 'Monthly_Grocery_Bill' in st.session_state: # check if previously answered
        default = st.session_state['Monthly_Grocery_Bill'] # use previous value
    else:
        default = 1 # use default
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
        default = st.session_state['Waste_Bag_Size']# use previous index of answer
    else:
        default = 0 # default is using first answer
    wastebag_size = st.radio("Which size of trashbag are you using?",  options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)
    
    # QUESTION FOR Waste Bag Count
    if 'Waste_Bag_Weekly_Count' in st.session_state: # check if previously answered
        default = st.session_state['Waste_Bag_Weekly_Count'] # use previous value
    else:
        default = 1 # use default
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
        default = 1 # use default
    tvpc = st.number_input("How many hours do you spend infront of the TV or PC per day?", min_value = 0, max_value = 24, value = default)
    
    # QUESTION FOR Internet usage
    if 'How_Long_Internet_Daily_Hour' in st.session_state: # check if previously answered
        default = st.session_state['How_Long_Internet_Daily_Hour'] # use previous value
    else:
        default = 1 # use default
    internet = st.number_input("How many hours do you use the internet per day?", min_value = 0, max_value = 24, value = default)
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    with col1:
       Back = st.button("Back")
    
    if Next:
        st.session_state['How_Often_Shower'] = shower
        st.session_state['Social_Activity'] = social
        st.session_state['Monthly_Grocery_Bill'] = groceries * 1.1 # Wechselkurs Euro to Dollar
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Waste_Bag_Size'] = wastebag_size
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        for rec in recycle_options:
            st.session_state['Recycling_' + rec] = 1 if rec in recycle else 0
        st.session_state['How_Long_TV_PC_Daily_Hour'] = tvpc
        st.session_state['How_Long_Internet_Daily_Hour'] = internet
        
        st.session_state['page'] = 'survey_energy'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_demo'
        st.rerun()

def dt_survey_energy():
    st.title("Carbon Footpint Questionnaire")
    st.header("Energy efficiency")
    
    st.write("How enegery efficient are you already?")
    
    # QUESTION FOR Energy of you heating source
    heat_options = ["coal", "electricity", "natural gas", "wood"] # define options
    if 'Heating_Energy_Source' in st.session_state: # check if question has been nswered yet
        default = heat_options.index(st.session_state['Heating_Energy_Source']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    energy = st.radio("What is your main source of engery for heating?", options = heat_options, horizontal = True, index = default)
    
    # QUESTION FOR your cooking appliences
    cooking_options = ["Stove", "Oven", "Microwave", "Grill"]
    default = []
    if 'Cooking_With_Stove' in st.session_state:
        for cook in cooking_options:
            if st.session_state['Cooking_With_' + cook] == 1:
                default.append(cook)
    cooking = st.multiselect("Which of the following appliances do you use for cooking?", options = cooking_options, default = default)
    
    # QUESTION FOR energy efficiency
    questOptions = ["Yes", "Sometimes", "No"] # define options
    if 'Energy_efficiency' in st.session_state: # check if question has been nswered yet
        default = st.session_state['Energy_efficiency'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    energy_eff = st.radio("Would you consider your electric appliances as energy efficient?", options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Next")
    with col1:
       Back = st.button("Back")

    if Next:
        for hot in heat_options:
            st.session_state['Heating_Energy_Source_' + hot] = 1 if hot == energy else 0
        for cook in cooking_options:
            st.session_state['Cooking_With_' + cook] = 1 if cook in cooking else 0
        st.session_state['Energy_efficiency'] = energy_eff
        
        st.session_state['page'] ='survey_travel'
        st.rerun()
    if Back:
        st.session_state['page'] = 'survey_life'
        st.rerun()
                
def dt_survey_travel():
    st.title("Carbon Footpint Questionnaire")
    st.header("Travelling")
    
    st.write("Lastly, some question about yout means of getting around and how much you travel.")
    
    # QUESTION FOR main means of transportations
    trans_options = ["walk/bicycle", "public", "petrol", "diesel", "electric", "hybrid", "lpg"]# define options
    if 'Transport' in st.session_state: # check if question has been nswered yet
        default = trans_options.index(st.session_state['Transport']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    transport = st.radio("What is your main method of transportation?", options = trans_options, horizontal = False, index = default)
   
    # QUESTION FOR distance traveled monthly
    if 'Vehicle_Monthly_Distance_Km' in st.session_state: # check if previously answered
        default = st.session_state['Vehicle_Monthly_Distance_Km'] # use previous value
    else:
        default = 1 # use default
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Frequency of plane usage
    questOptions = ["never", "rarely", "frequently", "very frequently"] # define options
    if 'Frequency_of_Traveling_by_Air' in st.session_state: # check if question has been nswered yet
        default = st.session_state['Frequency_of_Traveling_by_Air'] # use previous index of answer
    else:
        default = 0 # default is using first answer
    plane = st.radio("How often did you travel by plane in the last month?", options = range(len(questOptions)), format_func=questOptions.__getitem__, horizontal = True, index = default)

    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Show Results")
    with col1:
       Back = st.button("Back")

    if Next:
         for car in trans_options:
             st.session_state['Transport_' + car] = 1 if car == transport else 0
             st.session_state['Vehicle_Type_' + car] = 1 if car == transport else 0
         if trans_options.index(transport) > 1:
             st.session_state['Transport_private'] = 1
         else:
             st.session_state['Transport_private'] = 0
         st.session_state['Vehicle_Monthly_Distance_Km'] = km
         st.session_state['Frequency_of_Traveling_by_Air'] = plane
         
         st.session_state['page'] ='results'
         st.rerun()
    if Back:
         st.session_state['page'] = 'survey_energy'
         st.rerun()

def dt_results():
    st.title("Carbon Footpint Questionnaire")
    st.header("Results")

    ordinalVar=['Body_Type', 'Diet', 'How_Often_Shower', 'Social_Activity', 'Frequency_of_Traveling_by_Air',
                'Waste_Bag_Size', 'Energy_efficiency']
    numVar = ['Monthly_Grocery_Bill','Vehicle_Monthly_Distance_Km', 'Waste_Bag_Weekly_Count', 'How_Long_TV_PC_Daily_Hour',
              'How_Many_New_Clothes_Monthly',  'How_Long_Internet_Daily_Hour']
    restVar = ['Transport_walk/bicycle', 'Recycling_Glass', 'Recycling_Plastic',
       'Heating_Energy_Source_natural gas', 'Cooking_With_Grill',
       'Recycling_Metal', 'Heating_Energy_Source_wood', 'Cooking_With_Stove',
       'Cooking_With_Oven', 'Heating_Energy_Source_electricity',
       'Cooking_With_Microwave', 'Transport_private', 'Vehicle_Type_electric',
       'Vehicle_Type_lpg', 'Heating_Energy_Source_coal', 'Transport_public',
       'Sex_female', 'Vehicle_Type_petrol', 'Vehicle_Type_hybrid',
       'Recycling_Paper', 'Vehicle_Type_diesel']
    
    all_names = numVar + ordinalVar + restVar
    
    data = pd.DataFrame([[st.session_state['Monthly_Grocery_Bill'],
        st.session_state['Vehicle_Monthly_Distance_Km'],
        st.session_state['Waste_Bag_Weekly_Count'],
        st.session_state['How_Long_TV_PC_Daily_Hour'],
        st.session_state['How_Many_New_Clothes_Monthly'],
        st.session_state['How_Long_Internet_Daily_Hour'],
        
        st.session_state['Body_Type'],
        st.session_state['Diet'],
        st.session_state['How_Often_Shower'],
        st.session_state['Social_Activity'],
        st.session_state['Frequency_of_Traveling_by_Air'],
        st.session_state['Waste_Bag_Size'],
        st.session_state['Energy_efficiency'],
     
        st.session_state['Transport_walk/bicycle'],
        st.session_state['Recycling_Glass'],
        st.session_state['Recycling_Plastic'],
        st.session_state['Heating_Energy_Source_natural gas'],
        st.session_state['Cooking_With_Grill'],
        st.session_state['Recycling_Metal'],
        st.session_state['Heating_Energy_Source_wood'],
        st.session_state['Cooking_With_Stove'],
        st.session_state['Cooking_With_Oven'],
        st.session_state['Heating_Energy_Source_electricity'],
        st.session_state['Cooking_With_Microwave'],
        st.session_state['Transport_private'],
        st.session_state['Vehicle_Type_electric'],
        st.session_state['Vehicle_Type_lpg'],
        st.session_state['Heating_Energy_Source_coal'],
        st.session_state['Transport_public'],
        st.session_state['Sex'],
        st.session_state['Vehicle_Type_petrol'],
        st.session_state['Vehicle_Type_hybrid'],
        st.session_state['Recycling_Paper'],
        st.session_state['Vehicle_Type_diesel']]], columns=all_names)
    
    
    #st.write(X)
    #st.write(model.coef_)
    
    prediction = model_dt.predict(data)
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue = max(prediction[0],0)
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
    
    
 #   colWidth = get_width(html=container_width_js)
  #  earth_width = min(colWidth , int(earths*earth.shape[1]*0.1))
   
    st.image(earthsImage[:,range(int(earths*earth.shape[1])),:], channels="RGB", output_format="auto",width = None)
    
    
    if st.button("Show How to Improve"):
         st.session_state['prediction'] = predValue
         st.session_state['dataX'] = data
         st.session_state['page'] ='improve'
         st.rerun()
    
def dt_improvement():
    
    dataX = st.session_state['dataX']
 #   X_weighted = np.multiply(dataX.iloc[0], model.best_estimator_.feature_importances_)
    X_weighted = model_dt.best_estimator_.feature_importances_
    Xsorted = np.sort(X_weighted)
    features = dataX.columns

    n = 7
    topValues = Xsorted[(-1*n):]

    ordinalVar=['Body_Type', 'Diet', 'How_Often_Shower', 'Social_Activity', 'Frequency_of_Traveling_by_Air',
                'Waste_Bag_Size', 'Energy_efficiency']
    numVar = ['Monthly_Grocery_Bill','Vehicle_Monthly_Distance_Km', 'Waste_Bag_Weekly_Count', 'How_Long_TV_PC_Daily_Hour',
              'How_Many_New_Clothes_Monthly',  'How_Long_Internet_Daily_Hour']
    restVar = ['Transport_walk/bicycle', 'Recycling_Glass', 'Recycling_Plastic',
       'Heating_Energy_Source_natural gas', 'Cooking_With_Grill',
       'Recycling_Metal', 'Heating_Energy_Source_wood', 'Cooking_With_Stove',
       'Cooking_With_Oven', 'Heating_Energy_Source_electricity',
       'Cooking_With_Microwave', 'Transport_private', 'Vehicle_Type_electric',
       'Vehicle_Type_lpg', 'Heating_Energy_Source_coal', 'Transport_public',
       'Sex_female', 'Vehicle_Type_petrol', 'Vehicle_Type_hybrid',
       'Recycling_Paper', 'Vehicle_Type_diesel']

    topfeatures = []
    for i in topValues:
        ind = np.where(X_weighted == i)
        quest = features[ind][0]
        if quest in restVar:
            quest = quest.split('_')
        topfeatures.append(quest)
        
    all_names = numVar + ordinalVar + restVar
    
    st.title("Carbon Footpint Questionnaire")
    
    st.write("Your current, monthly Carbon Footprint before applying any changes is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(st.session_state['prediction'])) + " " + unit.translate(SUB))
    
      
    st.header("How to improve your score:")
 
 
    if all_names[7] in topfeatures:
        questOptions = ["vegan", "vegetarian", "pescatarian", "omnivore"]
        diet_new = st.select_slider("Consider eating less animal products: ", options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['Diet'])
    else:
        diet_new = st.session_state['Diet']
   
    if all_names[8] in topfeatures:
        questOptions = ["less than daily", "daily", "twice a day", "more frequently"]
        shower_new = st.select_slider("Consider showering less frquently: ", options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['How_Often_Shower'])
    else:
        shower_new = st.session_state['How_Often_Shower']
    
    if all_names[9] in topfeatures:
        questOptions = ["never","sometimes", "often"]
        social_new = st.select_slider("Consider to reduce unnecessary social activities: ", options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['Social_Activity'])
    else:
        social_new = st.session_state['Social_Activity']
   
    if all_names[10] in topfeatures:
        questOptions = ["never", "rarely", "frequently", "very frequently"]
        plane_new = st.select_slider("Consider travelling less by plane: ", options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['Frequency_of_Traveling_by_Air'])
    else: 
        plane_new = st.session_state['Frequency_of_Traveling_by_Air']
  
    if all_names[11] in topfeatures:
        questOptions = ["small", "medium", "large", "extra large"]
        wastebag_size_new = st.select_slider("Consider smaller waste bags: ",  options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['Waste_Bag_Size'])
    else: 
        wastebag_size_new = st.session_state['Waste_Bag_Size']
   
    if all_names[12] in topfeatures:
        questOptions = ["Yes", "Sometimes", "No"]
        energy_eff_new = st.select_slider("Consider replacing less efficient appliences: ",  options = range(len(questOptions)), format_func=questOptions.__getitem__, value = st.session_state['Energy_efficiency'])
    else:
        energy_eff_new = st.session_state['Energy_efficiency']
   
    
    if all_names[16] in topfeatures or all_names[19] in topfeatures or all_names[22] in topfeatures or all_names[27] in topfeatures:
        heat_options = ["electricity", "wood", "natural gas", "coal"]
        prev_heat_options = [st.session_state['Heating_Energy_Source_electricity'],st.session_state['Heating_Energy_Source_wood'],st.session_state['Heating_Energy_Source_natural gas'],st.session_state['Heating_Energy_Source_coal']]
        prev_heat = [s for i, s in zip(prev_heat_options, heat_options) if i == 1]
        heating_new = st.selectbox("Consider switching to a greener energy source: ", options = heat_options, value = prev_heat[0])
    else:
        heat_options = ["electricity", "wood", "natural gas", "coal"]
        prev_heat_options = [st.session_state['Heating_Energy_Source_electricity'],st.session_state['Heating_Energy_Source_wood'],st.session_state['Heating_Energy_Source_natural gas'],st.session_state['Heating_Energy_Source_coal']]
        prev_heat = [s for i, s in zip(prev_heat_options, heat_options) if i == 1]
        heating_new = prev_heat[0]
    heat_new = {}
    for hot in heat_options:
        heat_new[hot] = 1 if hot == heating_new else 0
    
    
    if all_names[13] in topfeatures or all_names[24] in topfeatures or all_names[25] in topfeatures or all_names[26] in topfeatures or all_names[28] in topfeatures or all_names[30] in topfeatures or all_names[31] in topfeatures or all_names[33] in topfeatures:
        trans_options = ['walk/bicycle', 'public', 'petrol', 'diesel', 'electric', 'hybrid', 'lpg']
        prev_trans_options = [st.session_state['Transport_walk/bicycle'],
                              st.session_state['Transport_public'],
                              st.session_state['Transport_petrol'],
                              st.session_state['Transport_diesel'],
                              st.session_state['Transport_electric'],
                              st.session_state['Transport_hybrid'],
                              st.session_state['Transport_lpg']]
        prev_trans = [s for i, s in zip(prev_trans_options, trans_options) if i == 1]
        transport_new = st.selectbox("Consider switching to a better way of transportation: ", options = trans_options, index = prev_trans[0])
    else:
        trans_options = ['walk/bicycle', 'public', 'petrol', 'diesel', 'electric', 'hybrid', 'lpg']
        prev_trans_options = [st.session_state['Transport_walk/bicycle'],st.session_state['Transport_public'],st.session_state['Transport_petrol'],st.session_state['Transport_diesel'],st.session_state['Transport_electric'],st.session_state['Transport_hybrid'],st.session_state['Transport_lpg']]
        prev_trans =[s for i, s in zip(prev_trans_options, trans_options) if i == 1]
        transport_new = prev_trans[0]
    trans_new = {}
    for car in trans_options:
        trans_new[car] = 1 if car == transport_new else 0
    if trans_options.index(prev_trans[0]) > 1:
        private_new = 1
    else:
        private_new = 0
    
    if all_names[0] in topfeatures:
        groceries_new = st.slider("Consider buying less groceries: ", 0, st.session_state['Monthly_Grocery_Bill']/1.1, st.session_state['Monthly_Grocery_Bill']/1.1) *1.1
    else:    
        groceries_new = st.session_state['Monthly_Grocery_Bill']
    if all_names[1] in topfeatures:
        km_new = st.slider("Consider to travel less: ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    else:
        km_new = st.session_state['Vehicle_Monthly_Distance_Km']
    if all_names[2] in topfeatures:
        wastebag_count_new = st.slider("Consider producing less waste: ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
    else:
        wastebag_count_new = st.session_state['Waste_Bag_Weekly_Count']
    if all_names[3] in topfeatures:
        tvpc_new = st.slider("Consider spending less time infront of the TV/PV: ", 0, st.session_state['How_Long_TV_PC_Daily_Hour'], st.session_state['How_Long_TV_PC_Daily_Hour'])
    else: 
        tvpc_new = st.session_state['How_Long_TV_PC_Daily_Hour']
    if all_names[4] in topfeatures:
        clothes_new = st.slider("Consider buying less new clothes: ", 0, st.session_state['How_Many_New_Clothes_Monthly'], st.session_state['How_Many_New_Clothes_Monthly'])
    else:
        clothes_new = st.session_state['How_Many_New_Clothes_Monthly']
    if all_names[5] in topfeatures:
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

    data_new = pd.DataFrame([[groceries_new,
      km_new,
      wastebag_count_new,
      tvpc_new,
      clothes_new,
      internet_new,
      st.session_state['Body_Type'],                       
      
      diet_new,
      shower_new,
      social_new,
      plane_new,
      wastebag_size_new,
      energy_eff_new,
      
      trans_new["walk/bicycle"],
      recycle_new_glass,
      recycle_new_plastic,
      heat_new["natural gas"],
      cooking_new_grill,
      recycle_new_metal,
      heat_new["wood"],
      cooking_new_stove,
      cooking_new_oven,
      heat_new["electricity"],
      cooking_new_microwave,
      private_new,
      trans_new["electric"],
      trans_new["lpg"],
      heat_new["coal"],
      trans_new["public"],
      st.session_state['Sex'],
      trans_new["petrol"],
      trans_new["hybrid"],
      recycle_new_paper,
      trans_new["diesel"]]], columns=all_names)
    
    prediction_new = model_dt.predict(data_new)
    st.write("If you would apply these change, your new, monthly Carbon Footprint would be:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue_new = max(prediction_new[0],0)
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
    fig.add_vline(x=prediction_new[0], line_width=3, line_dash="solid", line_color="green")
    fig.add_vline(x=st.session_state['prediction'], line_width=3, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
   

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
    st.header("10 Questions")
    st.write("This short version of the questionnaire, only has 10 questions.")
    
    # QUESTION FOR SEX
    sexOptions = ["female", "male"] # define options
    if 'Sex' in st.session_state: # check if question has been nswered yet
        default = sexOptions.index(st.session_state['Sex']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    sex = st.radio("Sex:", options = sexOptions, horizontal = True, index = default)
    
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
    
    # QUESTION FOR Groceries
    if 'Monthly_Grocery_Bill' in st.session_state: # check if previously answered
        default = st.session_state['Monthly_Grocery_Bill'] # use previous value
    else:
        default = 1 # use default
    groceries = st.number_input("How much do you spend on groceries in a month (in Euro)?", min_value = 0, max_value = int(1e6), value = default)
    
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
        default = 1 # use default
    wastebag_count = st.number_input("How many bags of waste do you produce per week?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Internet usage
    if 'How_Long_Internet_Daily_Hour' in st.session_state: # check if previously answered
        default = st.session_state['How_Long_Internet_Daily_Hour'] # use previous value
    else:
        default = 1 # use default
    internet = st.number_input("How many hours do you use the internet per day?", min_value = 0, max_value = 24, value = default)
    
    heatOptions = ["coal", "electricity", "natural gas", "wood"] # define options
    if 'Heating_Energy_Source' in st.session_state: # check if question has been nswered yet
        default = heatOptions.index(st.session_state['Heating_Energy_Source']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    energy = st.radio("What is your main source of engery for heating?", options = heatOptions, horizontal = True, index = default)
    
    # QUESTION FOR main means of transportations
    transOptions = ["walk/bicycle", "public transport", "car (type: petrol)", "car (type: diesel)", "car (type: electric)", "car (type: hybrid)", "car (type: lpg)"]# define options
    if 'Transport' in st.session_state: # check if question has been nswered yet
        default = transOptions.index(st.session_state['Transport']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    transport = st.radio("What is your main method of transportation?", options = transOptions, horizontal = False, index = default)
   
    # QUESTION FOR distance traveled monthly
    if 'Vehicle_Monthly_Distance_Km' in st.session_state: # check if previously answered
        default = st.session_state['Vehicle_Monthly_Distance_Km'] # use previous value
    else:
        default = 1 # use default
    km =  st.number_input("How many kilometers do you travel per month?", min_value = 0, max_value = int(1e6), value = default)
   
    # QUESTION FOR Frequency of plane usage
    planeOptions = ["never", "rarely", "frequently", "very frequently"] # define options
    if 'Frequency_of_Traveling_by_Air' in st.session_state: # check if question has been nswered yet
        default = planeOptions.index(st.session_state['Frequency_of_Traveling_by_Air']) # use previous index of answer
    else:
        default = 0 # default is using first answer
    plane = st.radio("How often did you travel by plane in the last month?", options = planeOptions, horizontal = True, index = default)

    
  
    col1, col2, col3 = st.columns(3)
    with col3:
       Next = st.button("Show Results")
    
    if Next:
        
        for s in sexOptions:
            st.session_state['Sex_' + s] = 1 if s == sex else 0
         
        st.session_state['How_Many_New_Clothes_Monthly'] = clothes
        st.session_state['Vehicle_Monthly_Distance_Km'] = km
        st.session_state['Waste_Bag_Weekly_Count'] = wastebag_count
        st.session_state['Monthly_Grocery_Bill'] = groceries*1.1
        st.session_state['How_Long_Internet_Daily_Hour'] = internet

        for t in transOptions:
            st.session_state['Transport_Vehicle_Type_' + t] = 1 if t == transport else 0
            
        for f in planeOptions:
            st.session_state['Frequency_of_Traveling_by_Air_' + f] = 1 if f == plane else 0
            
        for h in heatOptions:
            st.session_state['Heating_Energy_Source_' + h] = 1 if h == energy else 0
        
        bmi = weight/((height/100)**2)
    
        st.session_state['Body_Type_overweight'] = 0; st.session_state['Body_Type_obese'] = 0;
        st.session_state['Body_Type_underweight'] = 0; st.session_state['Body_Type_normal'] = 0
        if bmi >= 30 :
           st.session_state['Body_Type_obese'] = 1
        elif bmi >= 25:
            st.session_state['Body_Type_overweight'] = 1
        elif bmi >= 18.5:
            st.session_state['Body_Type_normal'] = 1
        else:
            st.session_state['Body_Type_underweight'] = 1
       
        
        st.session_state['Height_tmp'] = height
        st.session_state['Weight_tmp'] = weight
        
        st.session_state['page'] = 'results'
        st.rerun()    
            
            
            
            
def lgbm_results():
    st.title("Carbon Footpint Questionnaire")
    st.header("Results")
    
    all_names = ['Sex_female', 
 'Sex_male',
 'How_Many_New_Clothes_Monthly',
 'Vehicle_Monthly_Distance_Km',
 'Waste_Bag_Weekly_Count',
 'Monthly_Grocery_Bill',
 'How_Long_Internet_Daily_Hour',
 'Transport_Vehicle_Type_electric',
 'Transport_Vehicle_Type_lpg',
 'Transport_Vehicle_Type_hybrid',
 'Transport_Vehicle_Type_diesel',
 'Transport_Vehicle_Type_petrol',
 'Transport_Vehicle_Type_walkbicycle',
 'Transport_Vehicle_Type_public',
 'Frequency_of_Traveling_by_Air_frequently',
 'Frequency_of_Traveling_by_Air_rarely',
 'Frequency_of_Traveling_by_Air_never',
 'Frequency_of_Traveling_by_Air_very_frequently',
 'Heating_Energy_Source_coal',
 'Heating_Energy_Source_natural_gas',
 'Heating_Energy_Source_wood',
 'Heating_Energy_Source_electricity',
 'Body_Type_overweight',
 'Body_Type_obese',
 'Body_Type_underweight',
 'Body_Type_normal']
    
    data = pd.DataFrame([[st.session_state['Sex_female'],
     st.session_state['Sex_male'],
     st.session_state['How_Many_New_Clothes_Monthly'],
     st.session_state['Vehicle_Monthly_Distance_Km'],
     st.session_state['Waste_Bag_Weekly_Count'],
     st.session_state['Monthly_Grocery_Bill'],
     st.session_state['How_Long_Internet_Daily_Hour'],
     
     st.session_state['Transport_Vehicle_Type_car (type: electric)'],
     st.session_state['Transport_Vehicle_Type_car (type: lpg)'],
     st.session_state['Transport_Vehicle_Type_car (type: hybrid)'],
     st.session_state['Transport_Vehicle_Type_car (type: diesel)'],
     st.session_state['Transport_Vehicle_Type_car (type: petrol)'],
     st.session_state['Transport_Vehicle_Type_walk/bicycle'],
     st.session_state['Transport_Vehicle_Type_public transport'],
     
     st.session_state['Frequency_of_Traveling_by_Air_frequently'],
     st.session_state['Frequency_of_Traveling_by_Air_rarely'],
     st.session_state['Frequency_of_Traveling_by_Air_never'],
     st.session_state['Frequency_of_Traveling_by_Air_very frequently'],
   
     st.session_state['Heating_Energy_Source_coal'],
     st.session_state['Heating_Energy_Source_natural gas'],
     st.session_state['Heating_Energy_Source_wood'],
     st.session_state['Heating_Energy_Source_electricity'],
     
     st.session_state['Body_Type_overweight'],
     st.session_state['Body_Type_obese'],
     st.session_state['Body_Type_underweight'],
     st.session_state['Body_Type_normal']]], columns=all_names)
       
    prediction = model_lgbm.predict(data)
    st.write("Your current, monthly Carbon Footprint is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue = max(prediction[0],0)
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
    st.image(earthsImage[:,range(int(earths*earth.shape[1])),:], channels="RGB", output_format="auto",width = None)
    
    
    if st.button("Show How to Improve"):
         st.session_state['prediction'] = predValue
         st.session_state['dataX'] = data
         st.session_state['page'] ='improve'
         st.rerun()
    
def lgbm_improvement():
    
    dataX = st.session_state['dataX']
    X_weighted = np.multiply(dataX.iloc[0], model_lgbm.feature_importances_)
    Xsorted = np.sort(X_weighted)
    features = model_lgbm.feature_name_

    n = 5
    topValues = Xsorted[(-1*n):]
    topfeatures = []
    for i in topValues:
        ind = np.where(X_weighted == i)[0].astype(int)[0]
        quest = features[ind]
        topfeatures.append(quest)
        
        all_names = ['Sex_female', 
     'Sex_male',
     'How_Many_New_Clothes_Monthly',
     'Vehicle_Monthly_Distance_Km',
     'Waste_Bag_Weekly_Count',
     'Monthly_Grocery_Bill',
     'How_Long_Internet_Daily_Hour',
     'Transport_Vehicle_Type_electric',
     'Transport_Vehicle_Type_lpg',
     'Transport_Vehicle_Type_hybrid',
     'Transport_Vehicle_Type_diesel',
     'Transport_Vehicle_Type_petrol',
     'Transport_Vehicle_Type_walkbicycle',
     'Transport_Vehicle_Type_public',
     'Frequency_of_Traveling_by_Air_frequently',
     'Frequency_of_Traveling_by_Air_rarely',
     'Frequency_of_Traveling_by_Air_never',
     'Frequency_of_Traveling_by_Air_very_frequently',
     'Heating_Energy_Source_coal',
     'Heating_Energy_Source_natural_gas',
     'Heating_Energy_Source_wood',
     'Heating_Energy_Source_electricity',
     'Body_Type_overweight',
     'Body_Type_obese',
     'Body_Type_underweight',
     'Body_Type_normal']
    
    st.title("Carbon Footpint Questionnaire")
    
    st.write("Your current, monthly Carbon Footprint before applying any changes is:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    st.header(str(round(st.session_state['prediction'])) + " " + unit.translate(SUB))

    st.header("How to improve your score:")
 
    
    if any(e in all_names[14:18] for e in topfeatures):
        plane_options = ["never", "rarely", "frequently", "very frequently"]
        prev_plane_options = [st.session_state['Frequency_of_Traveling_by_Air_never'], st.session_state['Frequency_of_Traveling_by_Air_rarely'], st.session_state['Frequency_of_Traveling_by_Air_frequently'], st.session_state['Frequency_of_Traveling_by_Air_very frequently']]
        prev_plane = [s for i, s in zip(prev_plane_options, plane_options) if i == 1]
        airtravel_new = st.select_slider("Consider travelling less by plane: ", options = plane_options, value = prev_plane)
    else: 
        plane_options = ["never", "rarely", "frequently", "very frequently"]
        prev_plane_options = [st.session_state['Frequency_of_Traveling_by_Air_never'], st.session_state['Frequency_of_Traveling_by_Air_rarely'], st.session_state['Frequency_of_Traveling_by_Air_frequently'], st.session_state['Frequency_of_Traveling_by_Air_very frequently']]
        prev_plane = [s for i, s in zip(prev_plane_options, plane_options) if i == 1]
        airtravel_new = prev_plane[0]
    plane_new = {}
    for fly in plane_options:
        plane_new[fly] = 1 if fly == airtravel_new else 0
   
    
   
    if  any(e in all_names[7:14] for e in topfeatures):
        heat_options = ["electricity", "wood", "natural gas", "coal"]
        prev_heat_options = [st.session_state['Heating_Energy_Source_electricity'],st.session_state['Heating_Energy_Source_wood'],
                             st.session_state['Heating_Energy_Source_natural gas'],st.session_state['Heating_Energy_Source_coal']]
        prev_heat = [s for i, s in zip(prev_heat_options, heat_options) if i == 1]
        heating_new = st.selectbox("Consider switching to a greener energy source: ", options = heat_options, value = prev_heat[0])
    else:
        heat_options = ["electricity", "wood", "natural gas", "coal"]
        prev_heat_options = [st.session_state['Heating_Energy_Source_electricity'],st.session_state['Heating_Energy_Source_wood'],
                             st.session_state['Heating_Energy_Source_natural gas'],st.session_state['Heating_Energy_Source_coal']]
        prev_heat = [s for i, s in zip(prev_heat_options, heat_options) if i == 1]
        heating_new = prev_heat[0]
    heat_new = {}
    for hot in heat_options:
        heat_new[hot] = 1 if hot == heating_new else 0
    

    if any(e in all_names[18:22] for e in topfeatures):
        trans_options =  ["walk/bicycle", "public transport", "car (type: petrol)", "car (type: diesel)", "car (type: electric)", "car (type: hybrid)", "car (type: lpg)"]
        prev_trans_options = [st.session_state['Transport_Vehicle_Type_walk/bicycle'], st.session_state['Transport_Vehicle_Type_public transport'],
                              st.session_state['Transport_Vehicle_Type_car (type: petrol)'],st.session_state['Transport_Vehicle_Type_car (type: diesel)'],
                              st.session_state['Transport_Vehicle_Type_car (type: electric)'],st.session_state['Transport_Vehicle_Type_car (type: hybrid)'],
                              st.session_state['Transport_Vehicle_Type_car (type: lpg)']]
        prev_trans = [s for i, s in zip(prev_trans_options, trans_options) if i == 1]
        transport_new = st.selectbox("Consider switching to a better way of transportation: ", options = trans_options, index = prev_trans[0])
    else:
        trans_options =  ["walk/bicycle", "public transport", "car (type: petrol)", "car (type: diesel)", "car (type: electric)", "car (type: hybrid)", "car (type: lpg)"]
        prev_trans_options = [st.session_state['Transport_Vehicle_Type_walk/bicycle'], st.session_state['Transport_Vehicle_Type_public transport'],
                              st.session_state['Transport_Vehicle_Type_car (type: petrol)'],st.session_state['Transport_Vehicle_Type_car (type: diesel)'],
                              st.session_state['Transport_Vehicle_Type_car (type: electric)'],st.session_state['Transport_Vehicle_Type_car (type: hybrid)'],
                              st.session_state['Transport_Vehicle_Type_car (type: lpg)']]
        prev_trans = [s for i, s in zip(prev_trans_options, trans_options) if i == 1]
        transport_new = prev_trans[0]
    trans_new = {}
    for car in trans_options:
      trans_new[car] = 1 if car == transport_new else 0
    

    if all_names[5] in topfeatures:
        groceries_new = st.slider("Consider buying less groceries: ", 0, st.session_state['Monthly_Grocery_Bill']/1.1, st.session_state['Monthly_Grocery_Bill']/1.1) *1.1
    else:    
        groceries_new = st.session_state['Monthly_Grocery_Bill']
 
    if all_names[3] in topfeatures:
        km_new = st.slider("Consider to travel less: ", 0, st.session_state['Vehicle_Monthly_Distance_Km'], st.session_state['Vehicle_Monthly_Distance_Km'])
    else:
       km_new = st.session_state['Vehicle_Monthly_Distance_Km']
   
    if all_names[4] in topfeatures:
        wastebag_count_new = st.slider("Consider producing less waste: ", 0, st.session_state['Waste_Bag_Weekly_Count'], st.session_state['Waste_Bag_Weekly_Count'])
    else:
        wastebag_count_new = st.session_state['Waste_Bag_Weekly_Count']
   
    if all_names[2] in topfeatures:
        clothes_new = st.slider("Consider buying less new clothes: ", 0, st.session_state['How_Many_New_Clothes_Monthly'], st.session_state['How_Many_New_Clothes_Monthly'])
    else:
        clothes_new = st.session_state['How_Many_New_Clothes_Monthly']
   
    if all_names[6] in topfeatures:
        internet_new = st.slider("Consider using the internet less: ", 0, st.session_state['How_Long_Internet_Daily_Hour'], st.session_state['How_Long_Internet_Daily_Hour'])
    else:
        internet_new = st.session_state['How_Long_Internet_Daily_Hour']

        

    data_new = pd.DataFrame([[st.session_state['Sex_female'],
     st.session_state['Sex_male'],
     
     clothes_new,
     km_new,
     wastebag_count_new,
     groceries_new,
     internet_new,
     
     trans_new['car (type: electric)'],
     trans_new['car (type: lpg)'],
     trans_new['car (type: hybrid)'],
     trans_new['car (type: diesel)'],
     trans_new['car (type: petrol)'],
     trans_new['walk/bicycle'],
     trans_new['public transport'],
     
     plane_new['frequently'],
     plane_new['rarely'],
     plane_new['never'],
     plane_new['very frequently'],
   
     heat_new['coal'],
     heat_new['natural gas'],
     heat_new['wood'],
     heat_new['electricity'],
     st.session_state['Body_Type_overweight'],
     st.session_state['Body_Type_obese'],
     st.session_state['Body_Type_underweight'],
     st.session_state['Body_Type_normal']]], columns=all_names)
    
    prediction_new = model_lgbm.predict(data_new)
    st.write("If you would apply these change, your new, monthly Carbon Footprint would be:")
    unit = "kgCO2e"
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    predValue_new = max(prediction_new[0],0)
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
    col1, col2, col3 = st.columns(3)
    with col1:
      Regression = st.button("Regression")
    with col3:
        RegShort = st.button("Regression (Short)")
  #  with col3:
   #    DecisionTree = st.button("Decision Tree")
       
    if Regression:
        st.session_state['model'] = 'regression'
        st.session_state['page'] = 'survey_welcome'
    elif RegShort:
        st.session_state['model'] = 'regShort'
        st.session_state['page'] = 'survey_welcome'
  #  elif DecisionTree:
   #     st.session_state['model'] = 'decision_tree'
    #    st.session_state['page'] = 'survey_welcome'        
        
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
         
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'survey_welcome':
            dt_survey_welcome()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'survey_demo':
            dt_survey_demo()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'survey_life':
            dt_survey_life()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'survey_energy':
            dt_survey_energy()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'survey_travel':
            dt_survey_travel()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'results':
            dt_results()
        elif st.session_state['model'] == 'decision_tree' and st.session_state['page'] == 'improve':
            dt_improvement()

if __name__ == '__main__':
 #  st.write("App started")
   main()