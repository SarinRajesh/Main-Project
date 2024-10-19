import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib  # Add this import

# Load the dataset
data = pd.read_csv('data/colors.csv')

# Extract RGB values and color names
X = data[['R', 'G', 'B']]
y = data['ColorName1']  # Use ColorName1 for the color names

# Normalize the RGB values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Print the shape of the data
print(f"Data shape: {X.shape}")
print(f"Sample data:\n{X.head()}")
print(f"Sample labels:\n{y.head()}")

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Create and train the KNN classifier
knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='euclidean')
knn.fit(X_train, y_train)

# Print model parameters
print(f"Model parameters: {knn.get_params()}")

# Make predictions on the test set
y_pred = knn.predict(X_test)

# Calculate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy * 100:.2f}%')

# Save the trained model and scaler
joblib.dump(knn, 'data/knn_model.joblib')
joblib.dump(scaler, 'data/scaler.joblib')
print("Model and scaler saved successfully.")

# Example usage: Predict the color of a new RGB value
new_color = [[93, 138, 168]]  # Example RGB value
new_color_scaled = scaler.transform(new_color)
predicted_color = knn.predict(new_color_scaled)
print(f'The predicted color is: {predicted_color[0]}')
