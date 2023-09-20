import os
import streamlit as st
from PIL import Image
import cv2
from extract_clothes_edges import extract_edges
from inference import get_demo_images
import streamlit as st
from PIL import Image
import os



human_image_names = sorted([fn[:-4] for fn in os.listdir('dataset/test_img')])
cloth_image_names = sorted([fn[:-4] for fn in os.listdir('dataset/test_clothes')])

st.title('Virtual-Try-On Demo')

col1, col2, col3 = st.columns(3)
with col1:
    human_image_name = st.selectbox("Choose a Human Image", human_image_names)
    human_file = f'dataset/test_img/{human_image_name}.png'
    if not os.path.exists(human_file):
        human_file = human_file.replace('.png', '.jpg')
    st.warning("Select a Human Image in the side for Virtual-Try-On")

    human = Image.open(human_file)
    human.save('dataset/test_img/input.png')
    st.image(human, width=150)

with col2:
    cloth_image_name = st.selectbox("Choose a Clothes Image", cloth_image_names)
    cloth_file = f'dataset/test_clothes/{cloth_image_name}.jpg'
    # if not os.path.exists(cloth_file):
    #     cloth_file = cloth_file.replace('.jpg', '.png')
    st.warning("Select a Clothes Image in the side for Virtual-Try-On")
    cloth = Image.open(cloth_file)
    cloth.save('dataset/test_clothes/cloth.jpg')
    extract_edges(demo=True)
    st.image(cloth, width=150)

result_images = get_demo_images()
st.image(result_images, width=300)

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