import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# ------------------------ Styling Setup ------------------------
sns.set_theme(style='whitegrid')  # clean modern grid style
plt.rcParams.update({
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.titlepad': 15,
    'figure.dpi': 100,
    'grid.alpha': 0.3
})

# ------------------------ Load Dataset ------------------------
df = pd.read_excel('/rawData.xlsx')

print(df.info())
print(df.describe())

# ------------------------ Data Cleaning ------------------------
df_clean = df.copy()
df_clean[['latitude', 'longitude']] = df_clean[['latitude', 'longitude']].replace(-1.0, np.nan)
print("\nMissing values before cleaning:")
print(df_clean.isnull().sum())

df_clean = df_clean.fillna({'latitude': df_clean['latitude'].mean(), 'longitude': df_clean['longitude'].mean()})
df_clean = df_clean[df_clean['state_name'].notna()]

str_cols = ['inout_travelling', 'operator', 'network_type', 'calldrop_category', 'state_name']
for col in str_cols:
    df_clean[col] = df_clean[col].str.strip().str.title()

print("\nMissing values after cleaning:")
print(df_clean.isnull().sum())

print("\nCleaned DataFrame preview:")
print(df_clean.head())

# ------------------------ Visualizations ------------------------

# 1. Rating Distribution
plt.figure(figsize=(8, 5))
sns.countplot(data=df_clean, x='rating', palette='viridis')
plt.title('Rating Distribution')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# 2. Call Drop Category Frequency
plt.figure(figsize=(10, 5))
sns.countplot(data=df_clean, y='calldrop_category', order=df_clean['calldrop_category'].value_counts().index, palette='magma')
plt.title('Call Drop Category Frequency')
plt.xlabel('Count')
plt.ylabel('Call Drop Category')
plt.tight_layout()
plt.show()

# 3. Operator-wise Average Rating
plt.figure(figsize=(10, 5))
sns.barplot(data=df_clean, x='operator', y='rating', ci=None, palette='Set2')
plt.title('Operator-wise Average Rating')
plt.xlabel('Operator')
plt.ylabel('Average Rating')
plt.tight_layout()
plt.show()

# 4. Monthly Trend of Ratings
plt.figure(figsize=(10, 5))
sns.lineplot(data=df_clean, x='month', y='rating', hue='year', marker='o', palette='tab10')
plt.title('Monthly Trend of Ratings')
plt.xlabel('Month')
plt.ylabel('Average Rating')
plt.tight_layout()
plt.show()

# 5. Average Rating by State
main_states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Uttar Pradesh', 'Gujarat', 'Rajasthan']
df_states = df_clean[df_clean['state_name'].isin(main_states)]

plt.figure(figsize=(10, 5))
sns.barplot(data=df_states, x='state_name', y='rating', palette='cubehelix')
plt.title('Average User Rating by State')
plt.xlabel('State')
plt.ylabel('Average Rating')
plt.ylim(0, 5)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 6. Correlation Heatmap
plt.figure(figsize=(6, 4))
sns.heatmap(df_clean[['rating', 'latitude', 'longitude']].corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.show()

# 7. Call Drop Category by Operator
plt.figure(figsize=(10, 5))
sns.countplot(data=df_clean, x='operator', hue='calldrop_category', palette='husl')
plt.title('Call Drop Categories by Operator')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ------------------------ Normalization ------------------------
scaler = MinMaxScaler()
df_clean[['rating', 'latitude', 'longitude']] = scaler.fit_transform(df_clean[['rating', 'latitude', 'longitude']])
print("\nAfter Normalisation")
print(df_clean[['rating', 'latitude', 'longitude']].describe())

# 8. Scatter Plot - Longitude vs Rating
plt.figure(figsize=(8, 5))
plt.scatter(df_clean['longitude'], df_clean['rating'], alpha=0.5, color='steelblue')
plt.xlabel('Longitude (Normalized)')
plt.ylabel('Rating (Normalized)')
plt.title('Scatterplot: Longitude vs Rating')
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------ Simple Linear Regression ------------------------
x = df_clean[['longitude']]
y = df_clean['rating']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)

model = LinearRegression()
model.fit(x_train, y_train)

# Predict
long_norm = scaler.transform([[0, 20.5, 0]])[0][1]
check_location = pd.DataFrame({'longitude': [long_norm]})
result = model.predict(check_location)
print("Predicted Rating for Longitude 20.5: ", result[0])

# 9. Regression Line Plot
plt.figure(figsize=(8, 5))
plt.scatter(x, y, color="blue", alpha=0.4)
plt.plot(x, model.predict(x), color="red", linewidth=2)
plt.xlabel('Longitude (Normalized)')
plt.ylabel('Rating (Normalized)')
plt.title('Linear Regression Fit: Longitude vs Rating')
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------ Model Evaluation ------------------------
y_pred = model.predict(x_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error (MSE): {mse:.4f}")

# ------------------------ Key Findings ------------------------

# 1. Most users rated their experience between 3 to 5 stars, showing a skew towards positive ratings.
# 2. The 'Call Drop Category' varies significantly by operator, indicating differences in service quality.
# 3. Average rating trends fluctuate by month and year, suggesting seasonal or infrastructure effects.
# 4. States like Maharashtra and Karnataka report relatively higher user ratings than others.
# 5. A weak but noticeable correlation exists between longitude and user rating, confirmed by the regression fit.