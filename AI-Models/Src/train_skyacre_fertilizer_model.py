import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
import warnings
import joblib
import opendatasets as od
warnings.filterwarnings('ignore')

data = pd.read_csv('/content/crop-and-fertilizer-dataset-for-westernmaharashtra/Crop and fertilizer dataset.csv')
data.head(5)

encoder1, encoder2 = LabelEncoder(), LabelEncoder()
District = encoder1.fit_transform(data['District_Name'])
Soil = encoder2.fit_transform(data['Soil_color'])

crops = np.unique(data['Crop'].values)
map_crops = np.transpose([crops, [i for i in range(len(crops))]])
map_crops


fertilizers = np.unique(data['Fertilizer'].values)
map_fertilizers = np.transpose([fertilizers, [i for i in range(len(fertilizers))]])
map_fertilizers

X = np.column_stack((District, Soil, data.iloc[:, 2:8].values))
y = data.iloc[:, 8:].values

y_crop = []
for crop in y[:, 0]:
    for i in map_crops:
        if crop == i[0]:
            y_crop.append(i[1])

y_fert = []
for fert in y[:, 1]:
    for i in map_fertilizers:
        if fert == i[0]:
            y_fert.append(i[1])

y_numeric = np.transpose(np.array([y_crop, y_fert]))

X_train, X_test, y_train, y_test = train_test_split(X, y_numeric, test_size=0.25, random_state=42)


dt = DecisionTreeClassifier(random_state=42)
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)


joblib.dump(dt, "/Models/skyacre_fertilizer_model.pkl")