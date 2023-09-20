from inference import get_demo_images, get_upload_images
import streamlit as st
from PIL import Image
import os



st.title('Virtual-Try-On Demo')



with st.form('feedback_form'):
    st.header('Feedback form')

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input('Please enter your name')
        rating = st.slider('Please rate the demo', 0, 10, 5)
        des = st.text_input('Please enter your description')
    with col2:
        dob = st.date_input('Please enter your date of birth')
        recommend = st.radio('Would you recommend this demo to a friend?', ('Yes', 'No'))
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    st.write('**Name:**', name, '**Date of birth:**', dob, '**Rating:**', rating, '**Recommend:**', recommend, '**Description:**', des, '**Would recommend:**', recommend == 'Yes')