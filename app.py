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


col1, col2, col3 = st.columns(3)
with col1:
   st.session_state['Model_Regression'] = st.button("Regression")
with col2:
   st.session_state['Model_DK'] = st.button("Decision Tree")

if st.session_state['Model_Regression']:
    import app_regression
    model, encoder, cfdata = load_model_and_encoder()
    app_regression.main()
if st.session_state['Model_DK'] :
    import app_decisionTree
    model, cfdata = load_model_and_data()
    app_decisionTree.main()
#  #   st.write("App started")
#     main()
