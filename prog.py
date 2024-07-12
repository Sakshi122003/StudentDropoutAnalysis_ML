import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
from flask import Flask,render_template,request
import random

df = pd.read_csv('final sih.csv')

# Check for missing values
print(df.isnull().sum() / len(df) * 100)

# Encode categorical columns
label_encoder = LabelEncoder()
categorical_cols = ["School Wise", "Area Wise", "Gender Wise", "Caste Wise"]

for col in categorical_cols:
    df[col] = label_encoder.fit_transform(df[col])

# Define columns to drop
columns_to_drop = ['Father Occupation', 'Mother Occupation', 'Standards']

# Drop specified columns
df = df.drop(columns=columns_to_drop)

# Define input features and output variable
input_columns = ["School Wise", "Area Wise", "Gender Wise", "Caste Wise", "Age", "Monthly Income"]
output_column = "Dropped out"
data = df[input_columns]
target = df[output_column]

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, random_state=42)

# Create a Random Forest classifier
clf = RandomForestClassifier(random_state=42)

# Train the classifier on the training data
clf.fit(x_train, y_train)

# Make predictions on the test data
y_pred = clf.predict(x_test)


# Define custom labels for decoding predictions
custom_labels = {
    "School Wise": ["Primary", "Secondary", "Higher Secondary"],
    "Area Wise": df["Area Wise"].unique(),  # You can update this based on your dataset
    "Gender Wise": ["Male", "Female"],
    "Caste Wise": df["Caste Wise"].unique()  # You can update this based on your dataset
}

# Function to predict dropout status based on user input
def predict_dropout_status(input_features):
    input_features_encoded = []
    
    for col, val in zip(input_columns, input_features):
        if col in categorical_cols:
            if col not in custom_labels:
                raise ValueError(f"No custom labels found for categorical column: {col}")
            
            label_map = {label: idx for idx, label in enumerate(custom_labels[col])}
            
            if val not in label_map:
                raise ValueError(f"Invalid input value '{val}' for column '{col}'")
            
            input_features_encoded.append(label_map[val])
        else:
            input_features_encoded.append(val)
    
    predicted_dropout = clf.predict([input_features_encoded])
    return predicted_dropout[0]

# Example usage

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/details",methods=["POST"])
def details():
    if(request.method=="POST"):
        output = request.form.to_dict()
        age = output["fage"]
        caste = output["caste"]
        state = output["state"]
        education = output["Ed"]
        gender = request.form.get("gender")
        try:
            input_columns = ["age", "gender", "education"]
            categorical_cols = ["gender"]
            custom_labels = {
                "gender": ["Male", "Female"]
            }
            
            input_features = ["Primary", 1, "Male",0,age,random.randint(1000,100000)]
            predicted_status = predict_dropout_status(input_features)
            text1 = ""
            if(int(predicted_status)==1):
              text1 = "High Dropout Chances(80-100%)"
            else:
               text1 = "Low Dropout Chances(<80%)"

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

        return render_template("details.html",text=text1)

    else:
        return -1
app.run(debug=True,port=5001)


