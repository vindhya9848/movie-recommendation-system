import joblib
from sentence_transformers import SentenceTransformer

# load models
clf = joblib.load("../ml-notebooks/intent_classifier_lr.pkl")
label_encoder = joblib.load("../ml-notebooks/intent_label_encoder.pkl")
embedder = SentenceTransformer("../ml-notebooks/intent_embedder/")

def predict_intent(text):
    emb = embedder.encode([text], convert_to_numpy=True)
    pred_id = clf.predict(emb)[0]
    return label_encoder.inverse_transform([pred_id])[0]

# print(predict_intent("I feel low and drained today"))
# print(predict_intent("Recommend something fun"))
# print(predict_intent("I want something fantasy related , I like harry potter something like that"))


if __name__ == "__main__":
    print(predict_intent("I feel low and drained today"))
    print(predict_intent("Recommend something fun"))
    print(predict_intent("I want something fantasy related , I like harry potter something like that"))

