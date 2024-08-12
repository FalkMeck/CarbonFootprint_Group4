# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 13:58:57 2024

@author: falko
"""

import streamlit as st
#import pandas as pd
import pickle
import sklearn
#import numpy as np
import matplotlib.image as img
#import math
#import plotly.express as px

# st.write(sklearn.__version__)

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
def load_model_and_data():
    with open('tree.pkl', 'rb') as f:
        model_f = pickle.load(f)
    with open('CFdata.pkl', 'rb') as f:
        CFdata_f = pickle.load(f)
    return model_f, CFdata_f

@st.cache_resource
def load_earth_image():
    image = img.imread('earth.jpg') 
    return image

earth = load_earth_image()

if __name__ == '__main__':
    
    col1, col2, col3 = st.columns(3)
    with col3:
       Regression = st.button("Regression")
    with col1:
       DecisionTree = st.button("Decision Tree")
    
    if Regression:
        import app_regression
        model, encoder, cfdata = load_model_and_encoder()
        if 'page' not in st.session_state:
            st.session_state['page'] = 'survey_welcome'  

        if st.session_state['page'] == 'survey_welcome':
            app_regression.survey_welcome()
        elif st.session_state['page'] == 'survey_demo':
            app_regression.survey_demo()
        elif st.session_state['page'] == 'survey_life':
            app_regression.survey_life()
        elif st.session_state['page'] == 'survey_energy':
            app_regression.survey_energy()
        elif st.session_state['page'] == 'survey_travel':
            app_regression.survey_travel()
        elif st.session_state['page'] == 'results':
            app_regression.results()
        elif st.session_state['page'] == 'improve':
            app_regression.improvement()
        
        
    if DecisionTree:
        model, cfdata = load_model_and_data()
        import app_decisionTree
        app_decisionTree.main()
#  #   st.write("App started")
#     main()
