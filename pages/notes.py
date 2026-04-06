import streamlit as st
from PIL import Image
import numpy as np
import cv2
import pytesseract
import easyocr


reader = easyocr.Reader(['en'], gpu=False)

# Windows example
pytesseract.pytesseract.tesseract_cmd = r"C://Program Files//Tesseract-OCR//tesseract.exe"


# -------------------- Streamlit UI --------------------
st.title("Pump Display OCR Dashboard")

st.markdown("""
Take a photo of the pump display **or upload an existing image**. 
The app will preprocess the image and extract numbers automatically.
""")

# ---- CAMERA INPUT ----
camera_pic = st.camera_input("Take a photo")

# ---- FILE UPLOAD ----
uploaded_file = st.file_uploader("Or upload an existing image", type=None)  # allow HEIC, PNG, JPG, JPEG

# ---- SELECT IMAGE ----
image = None
if camera_pic is not None:
    image = Image.open(camera_pic)
elif uploaded_file is not None:
    image = Image.open(uploaded_file)

if image is not None:
    st.subheader("Input Image")
    st.image(image, use_column_width=True)

    # -------------------- Preprocessing --------------------

    img_cv = np.array(image)

    # --- ROI crop (tune this!) ---
    h, w = img_cv.shape[:2]
    roi = img_cv[int(h*0.35):int(h*0.75), int(w*0.15):int(w*0.85)]

    # --- grayscale ---
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # --- contrast enhancement ---
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # --- threshold ---
    _, thresh = cv2.threshold(gray, 0, 255,
                            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # --- morphology ---
    kernel = np.ones((3,3), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # --- resize ---
    resized = cv2.resize(processed, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

    results = reader.readtext(resized, detail=1)

    # Extract only numbers
    numbers = []
    for (bbox, text, prob) in results:
        cleaned = ''.join([c for c in text if c in '0123456789.'])
        if cleaned:
            numbers.append((cleaned, prob))

    st.subheader("Extracted Numbers (EasyOCR)")
    for num, prob in numbers:
        st.write(f"{num} (confidence: {prob:.2f})")

    # -------------------- Save Processed Image --------------------


# import streamlit as st
# from PIL import Image
# import numpy as np
# import cv2
# import pytesseract

# st.header("Take a photo of the pump display")

# # Capture image from camera
# pic = st.camera_input("Capture Pump Screen")

# if pic is not None:
#     # Convert Streamlit input to PIL Image
#     image = Image.open(pic)
#     st.image(image, caption="Captured Image", use_column_width=True)

#     # Convert to NumPy array for OpenCV
#     img_cv = np.array(image)

#     # Convert to grayscale
#     gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

#     # Apply thresholding for clearer digits
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#     # Optional: You can crop the region if your display is always in a fixed area
#     # cropped = thresh[y1:y2, x1:x2]

#     # OCR: Extract text
#     config = "--psm 6 digits"  # psm 6 = assume a uniform block of text; "digits" restricts OCR to numbers
#     text = pytesseract.image_to_string(thresh, config=config)

#     # Display extracted numbers
#     st.subheader("Extracted Numbers:")
#     st.text(text)

#     # Save the processed image if needed for ML
#     cv2.imwrite("processed_pump_image.png", thresh)
#     st.success("Saved processed_pump_image.png ✅")