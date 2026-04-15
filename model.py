import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

RFC_FOREST_DEPTH = 2


def train_model(X_train, y_train):
    model = RandomForestClassifier(
        max_depth=RFC_FOREST_DEPTH, n_estimators=5, random_state=1993
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test, float_precision=4):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }

    return json.loads(
        json.dumps(metrics), parse_float=lambda x: round(float(x), float_precision)
    )
