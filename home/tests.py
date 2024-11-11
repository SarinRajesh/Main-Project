import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

def plot_3d_color_space(X, y, title):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(X['R'], X['G'], X['B'], 
                        c=y, 
                        cmap='rainbow')
    
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_title(title)
    
    plt.colorbar(scatter)
    plt.show()

def plot_learning_curve(estimator, X, y, title):
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=5, n_jobs=-1, 
        train_sizes=np.linspace(0.1, 1.0, 10))
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_mean, label='Training score')
    plt.plot(train_sizes, test_mean, label='Cross-validation score')
    
    plt.fill_between(train_sizes, train_mean - train_std,
                     train_mean + train_std, alpha=0.1)
    plt.fill_between(train_sizes, test_mean - test_std,
                     test_mean + test_std, alpha=0.1)
    
    plt.xlabel('Training Examples')
    plt.ylabel('Score')
    plt.title(title)
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

def plot_confusion_matrix(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(rotation=45)
    plt.yticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_feature_importance(X, y_encoded):
    correlations = []
    for feature in X.columns:
        corr = np.corrcoef(X[feature], y_encoded)[0, 1]
        correlations.append(abs(corr))
    
    plt.figure(figsize=(8, 5))
    plt.bar(X.columns, correlations)
    plt.title('Feature Importance (Correlation with Target)')
    plt.xlabel('RGB Channels')
    plt.ylabel('Absolute Correlation')
    plt.show()

def test_color_model():
    # Create a simpler color dataset with basic colors (multiple samples per class)
    colors_data = {
        'ColorName1': [
            # Reds (3 samples each)
            'red', 'red', 'red',
            'dark_red', 'dark_red', 'dark_red',
            'light_red', 'light_red', 'light_red',
            
            # Greens
            'green', 'green', 'green',
            'dark_green', 'dark_green', 'dark_green',
            'light_green', 'light_green', 'light_green',
            
            # Blues
            'blue', 'blue', 'blue',
            'dark_blue', 'dark_blue', 'dark_blue',
            'light_blue', 'light_blue', 'light_blue',
            
            # Yellows
            'yellow', 'yellow', 'yellow',
            'dark_yellow', 'dark_yellow', 'dark_yellow',
            'light_yellow', 'light_yellow', 'light_yellow',
            
            # Purples
            'purple', 'purple', 'purple',
            'dark_purple', 'dark_purple', 'dark_purple',
            'light_purple', 'light_purple', 'light_purple'
        ] * 2,  # Duplicate all samples to increase dataset size
        'R': [
            # Reds
            255, 255, 255,
            139, 139, 139,
            255, 255, 255,
            
            # Greens
            0, 0, 0,
            0, 0, 0,
            144, 144, 144,
            
            # Blues
            0, 0, 0,
            0, 0, 0,
            135, 135, 135,
            
            # Yellows
            255, 255, 255,
            204, 204, 204,
            255, 255, 255,
            
            # Purples
            128, 128, 128,
            85, 85, 85,
            200, 200, 200
        ] * 2,  # Duplicate all samples
        'G': [
            # Reds
            0, 0, 0,
            0, 0, 0,
            102, 102, 102,
            
            # Greens
            255, 255, 255,
            100, 100, 100,
            238, 238, 238,
            
            # Blues
            0, 0, 0,
            0, 0, 0,
            206, 206, 206,
            
            # Yellows
            255, 255, 255,
            204, 204, 204,
            255, 255, 255,
            
            # Purples
            0, 0, 0,
            0, 0, 0,
            162, 162, 162
        ] * 2,  # Duplicate all samples
        'B': [
            # Reds
            0, 0, 0,
            0, 0, 0,
            102, 102, 102,
            
            # Greens
            0, 0, 0,
            0, 0, 0,
            144, 144, 144,
            
            # Blues
            255, 255, 255,
            139, 139, 139,
            235, 235, 235,
            
            # Yellows
            0, 0, 0,
            0, 0, 0,
            102, 102, 102,
            
            # Purples
            128, 128, 128,
            85, 85, 85,
            200, 200, 200
        ] * 2  # Duplicate all samples
    }
    
    # Create DataFrame
    data = pd.DataFrame(colors_data)
    
    # Prepare features (RGB values) and target (color names)
    X = data[['R', 'G', 'B']]
    y = data['ColorName1']
    
    # Add random noise to RGB values
    noise_level = 10
    X = X + np.random.normal(0, noise_level, X.shape)
    X = np.clip(X, 0, 255)
    
    # Normalize RGB values
    X = X / 255.0
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Plot 3D color space before splitting
    plot_3d_color_space(X, y_encoded, 'Color Distribution in RGB Space')
    
    # Plot feature importance
    plot_feature_importance(X, y_encoded)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, 
        test_size=0.3,
        random_state=42,
        stratify=y_encoded
    )
    
    # Train model
    knn = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
    knn.fit(X_train, y_train)
    
    # Plot learning curve
    plot_learning_curve(knn, X, y_encoded, 
                       'Learning Curve (KNN Color Classifier)')
    
    # Make predictions
    y_pred = knn.predict(X_test)
    
    # Plot confusion matrix
    plot_confusion_matrix(y_test, y_pred, 
                         label_encoder.classes_)
    
    # Calculate and print metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    accuracy = np.mean(y_test == y_pred)
    
    print("\nModel Performance Metrics:")
    print("--------------------------")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R-squared Score: {r2:.4f}")
    print(f"Accuracy: {accuracy:.4f}")
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                              target_names=label_encoder.classes_))

    # Test specific colors
    test_colors = pd.DataFrame([
        [1.0, 0.0, 0.0],    # Red
        [0.0, 1.0, 0.0],    # Green
        [0.0, 0.0, 1.0],    # Blue
        [1.0, 1.0, 0.0],    # Yellow
        [0.5, 0.5, 0.5]     # Gray
    ], columns=['R', 'G', 'B'])
    
    print("\nSample Color Predictions:")
    print("------------------------")
    for _, rgb in test_colors.iterrows():
        pred_encoded = knn.predict([rgb])[0]
        predicted_color = label_encoder.inverse_transform([pred_encoded])[0]
        print(f"RGB [{rgb['R']:.1f}, {rgb['G']:.1f}, {rgb['B']:.1f}]: "
              f"Predicted as {predicted_color.replace('_', ' ').title()}")

# Load color samples from images
def get_color_samples(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img.reshape(-1, 3)
    return pixels / 255.0

if __name__ == "__main__":
    test_color_model()