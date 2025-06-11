import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv('enriched_sample.csv')
df['label'] = ((df.seniority>=8)&(df.emp_bracket>=3)).astype(int)
X = df[['company_age','emp_bracket','seniority']]
y = df['label']
model = LogisticRegression().fit(X,y)
joblib.dump(model, 'model.joblib')
