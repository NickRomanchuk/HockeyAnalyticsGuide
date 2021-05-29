import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

data = pd.read_csv (r'C:\Users\nickr\OneDrive\Desktop\LLS_Blog\GoaltenderClutch\SituationalvsOverallSV%.csv')

coef, p = spearmanr(data['SV%'], data['ClutchSV%'])

print(data.sort_values(by=['Difference']))
print(data.describe())
print(data[data['Difference']<0].count())
print(data[(data['Difference'] >= -0.5) & (data['Difference'] <= 0.5)].count())

plt.scatter(data['ClutchSV%'], data['SV%'])
plt.show()
