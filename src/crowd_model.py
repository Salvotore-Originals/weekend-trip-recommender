import numpy as np
from sklearn.linear_model import LinearRegression

class CrowdPredictor:

    def __init__(self):
        hours = np.array(range(24)).reshape(-1, 1)
        crowd = np.array([10,10,10,10,10,20,40,60,80,90,100,90,
                          85,80,70,60,50,40,30,20,15,10,10,10])

        self.model = LinearRegression()
        self.model.fit(hours, crowd)

    def predict(self, hour):
        val = self.model.predict([[hour]])[0]

        if val > 80:
            return "High"
        elif val > 40:
            return "Medium"
        return "Low"