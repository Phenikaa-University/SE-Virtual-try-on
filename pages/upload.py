from inference import get_demo_images, get_upload_images
from extract_clothes_edges import extract_edges
import streamlit as st
from PIL import Image
import os



human_image_names = sorted([fn[:-4] for fn in os.listdir('dataset/upload_img')])

st.title('Virtual-Try-On Demo')
st.header('Upload your own images')

col1, col2, col3 = st.columns(3)
with col1:
    if st.checkbox("Upload a Human Image"):
        human_file = st.file_uploader("Upload a Human Image", type=["png", "jpg", "jpeg"])
        if human_file is None:
            human_file = 'dataset/upload_img/upload_img.png'
        st.warning("Upload a Human Image in the side for Virtual-Try-On")
        human = Image.open(human_file)
        human.save('dataset/upload_img/upload_img.png')
        st.image(human, width=150)

    if st.checkbox('Live camera'):
        photo = st.camera_input('Take a photo')
        st.warning("Take a photo in the side for Virtual-Try-On")
        if photo is not None:
            st.subheader('You:')
            photo = Image.open(photo)
            photo = photo.resize((192, 256))
            # params = get_params(opt, I.size)
            # transform = get_transform(opt, params)
            # transform_E = get_transform(opt, params, method=Image.NEAREST, normalize=False)
            # I_tensor = transform(I)
            st.image(photo, width=150)
            photo.save('dataset/upload_img/upload_img.png')

with col2:
    if st.checkbox("Upload a Clothes Image"):
        clothes_file = st.file_uploader("Upload a Clothes Image", type=["png", "jpg", "jpeg"])
        if clothes_file is None:
            clothes_file = 'dataset/upload_clothes/upload.jpg'

        st.warning("Upload a Cloth Image in the side for Virtual-Try-On")
        clothes = Image.open(clothes_file)
        clothes.save('dataset/upload_clothes/upload.jpg')
        extract_edges()
        st.image(clothes, width=150)
    if st.checkbox("Select a Clothes Image"):
        cloth_image_names = sorted([fn[:-4] for fn in os.listdir('dataset/test_clothes')])
        cloth_image_name = st.selectbox("Choose a Clothes Image", cloth_image_names)
        cloth_file = f'dataset/test_clothes/{cloth_image_name}.jpg'
        cloth = Image.open(cloth_file)
        cloth.save('dataset/upload_clothes/upload.jpg')
        extract_edges()
        st.image(cloth, width=150)
        st.warning("Select a Clothes Image in the side for Virtual-Try-On")

with col3:
    result_images = get_upload_images()

    st.write('Result')
    st.image(result_images, width=200)



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