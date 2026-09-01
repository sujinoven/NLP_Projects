from sklearn.naive_bayes import MultinomialNB

def build_model():
    return MultinomialNB(alpha=1.0)