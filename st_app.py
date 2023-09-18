import os
import streamlit as st
from PIL import Image
import cv2

from inference import get_demo_images, get_upload_images

human_image_names = sorted([fn[:-4] for fn in os.listdir('dataset/test_img')])

st.title('Virtual-Try-On Demo')



if st.sidebar.checkbox('Upload'):
    human_file = st.sidebar.file_uploader("Upload a Human Image", type=["png", "jpg", "jpeg"])
    if human_file is None:
        human_file = 'dataset/test_img/default.png'
else:
    human_image_name = st.sidebar.selectbox("Choose a Human Image", human_image_names)
    human_file = f'dataset/test_img/{human_image_name}.png'
    if not os.path.exists(human_file):
        human_file = human_file.replace('.png', '.jpg')
    st.warning("Upload a Human Image in the sidebar for Virtual-Try-On")

human = Image.open(human_file)
human.save('dataset/upload_img/upload_img.png')
st.sidebar.image(human, width=300)

result_images = get_upload_images()
st.image(result_images, width=600)

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

