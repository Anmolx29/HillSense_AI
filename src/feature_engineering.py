import numpy as np

def create_target(df):

    def soil_state(row):
        score = 0

        # add randomness (VERY IMPORTANT)
        noise = np.random.uniform(-1, 1)

        # moisture influence
        if row['moisture'] + noise < 30:
            score += 2

        # nutrients with noise
        if row['n'] + noise*5 < 50:
            score += 1
        if row['p'] + noise*5 < 40:
            score += 1
        if row['k'] + noise*5 < 40:
            score += 1

        # classification
        if score == 0:
            return 4
        elif score == 1:
            return np.random.choice([1,2,3])  # random deficiency
        elif score == 2:
            return np.random.choice([2,3])
        elif score == 3:
            return 3
        else:
            return 5

    df['soil_state'] = df.apply(soil_state, axis=1)

    return df