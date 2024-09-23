import pandas as pd
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os

# Function to extract color features from images
def extract_color_features(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return np.zeros(3)  # Return a default value if the image is not found

    image = cv2.imread(image_path)
    image = cv2.resize(image, (100, 100))  # Resize for consistency
    pixels = np.float32(image.reshape(-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, _, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    dominant_color = palette[0].astype(int)
    return dominant_color

# Load the dataset
csv_path = 'data/color_palette.csv'
df = pd.read_csv(csv_path)

# Construct the full path for images in the CSV
df['features'] = df['image_path'].apply(lambda x: extract_color_features(os.path.join('D:/INTMCA/Sem 9/Miniproject/ElegantDecor', x)))
X = np.array(df['features'].tolist())  # Feature matrix (RGB values)
y = df['dominant_color']  # Labels (colors)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

# Save the trained model
model_file_path = 'data/color_palette_model.pkl'
joblib.dump(model, model_file_path)

print("Model trained and saved successfully at:", model_file_path)
