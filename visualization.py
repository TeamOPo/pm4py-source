import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("excel-backup/all_0.csv")




# gca stands for 'get current axis'
ax = plt.gca()

df.plot(kind='line', x='Input', y='precision', ax=ax)
df.plot(kind='line', x='Input', y='num_pets', color='red', ax=ax)

plt.show()