import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
def train_models(X,y,seed=1):
    return {"logistic":LogisticRegression(max_iter=500,random_state=seed).fit(X,y),
            "tree":DecisionTreeClassifier(max_depth=6,random_state=seed).fit(X,y),
            "forest":RandomForestClassifier(n_estimators=50,max_depth=8,random_state=seed).fit(X,y)}
class PreventiveAllocator:
    def __init__(self,model,threshold=.5,max_wait=10): self.model=model; self.threshold=threshold; self.max_wait=max_wait
    def allow(self,features,wait_age=0):
        return wait_age>=self.max_wait or float(self.model.predict_proba([features])[0,1])<self.threshold
