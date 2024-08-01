import streamlit as st
import os
import time
import requests
import urllib
from urllib.parse import quote
import cv2
import numpy as np
from zipfile import ZipFile

def _create_directories(_directory):
    """
    Create directory to save images.
    """
    try:
        if not os.path.exists(_directory):
            os.makedirs(_directory)
            time.sleep(0.2)
    except OSError as e:
        if e.errno != 17:
            raise
    return

def _download_page(url):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        respData = str(resp.read())
        return respData
    except Exception as e:
        print(e)
        exit(0)

def download_and_resize(keyword, limit, directory, resize, resize_width, resize_height, color_mode, progress_callback):
    """
    Download images from Google, resize them, and save them directly to the specified folder.
    """
    _create_directories(directory)

    url = 'https://www.google.com/search?q=' + quote(
        keyword.encode('utf-8')) + '&biw=1536&bih=674&tbm=isch&sxsrf=ACYBGNSXXpS6YmAKUiLKKBs6xWb4uUY5gA:1581168823770&source=lnms&sa=X&ved=0ahUKEwioj8jwiMLnAhW9AhAIHbXTBMMQ_AUI3QUoAQ'
    raw_html = _download_page(url)

    end_object = -1
    count = -1
    while count < limit:
        while True:
            try:
                new_line = raw_html.find('"https://', end_object + 1)
                end_object = raw_html.find('"', new_line + 1)
                if new_line == -1 or end_object == -1:
                    break

                object_raw = raw_html[new_line + 1:end_object]

                if any(extension in object_raw for extension in {'.jpg', '.png', '.ico', '.gif', '.jpeg'}):
                    break
            except Exception as e:
                break
        try:
            r = requests.get(object_raw, allow_redirects=True, timeout=1)
            if 'html' not in str(r.content):
                file_extension = '.jpg'  # Assume all images are jpg
                file_name = f"{keyword}_{count + 1}{file_extension}"
                save_path = os.path.join(directory, file_name)

                img = cv2.imdecode(np.asarray(bytearray(r.content)), cv2.IMREAD_COLOR)
                if color_mode == 'Grayscale':
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                elif color_mode == 'Black and White':
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

                if resize:
                    resized_img = cv2.resize(img, (resize_width, resize_height))
                else:
                    resized_img = img

                if count!=-1:
                    cv2.imwrite(save_path, resized_img)
                count += 1

                # Update progress
                progress_callback(count, limit)

        except Exception as e:
            pass

def create_zip_file(directory):
    zip_file_path = directory + ".zip"
    with ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    return zip_file_path

# Streamlit UI
st.title("🌟 Image Downloader 🌟")
st.header("Download images from Google with options for resizing and color modes")
st.write(
    """
    **Welcome to the Image Downloader tool!** 

    This powerful tool allows you to download images from Google, resize them, and convert them into different color modes. Perfect for data extraction in machine learning and deep learning projects.
    """
)

keywords = st.text_input("Enter a keyword for images:")
num_images = st.number_input("Number of images to download:", min_value=1)

resize = st.checkbox("Resize Images", value=False)
resize_width = 100
resize_height = 100
if resize:
    resize_width = st.number_input("Resize Width:", min_value=100, value=100)
    resize_height = st.number_input("Resize Height:", min_value=100, value=100)

color_mode = st.selectbox("Select Color Mode:", ["RGB", "Grayscale", "Black and White"])

directory = st.text_input("Folder Name(e.g., images):")

if st.button("Extract Images"):
    if not directory:
        st.error("Please specify the directory to save images.")
    elif not keywords:
        st.error("Please enter a keyword for images.")
    else:
        st.info("To cancel the extraction, refresh the browser window.")
        progress_bar = st.progress(0)
        progress_text = st.empty()  # Placeholder for the progress text

        def update_progress(count, total):
            progress_percentage = count / total
            progress_bar.progress(progress_percentage)
            progress_text.text(f"Extracting {count}/{total} images")

        download_and_resize(keywords, num_images, directory, resize, resize_width, resize_height, color_mode, update_progress)
        
        zip_file_path = create_zip_file(directory)
        st.success(f"Extracted {num_images} images to {directory}")
        with open(zip_file_path, "rb") as fp:
            st.download_button(
                label="Download ZIP",
                data=fp,
                file_name=os.path.basename(zip_file_path),
                mime="application/zip"
            )
st.write(
    """
    ---
    <footer style="text-align: center; padding: 20px; font-size: 14px; color: #888;">
        Developed by [Nandeesh H U](mailto:10nandeeshhu@gmail.com) <br>
        Indian Institute of Technology Guwahati
    </footer>
    """,
    unsafe_allow_html=True
)
