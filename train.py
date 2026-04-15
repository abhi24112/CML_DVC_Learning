import json

import pandas as pd
from sklearn.model_selection import train_test_split

from metrics_and_plots import plot_confusion_matrix, save_metrics
from model import evaluate_model, train_model
from utils_and_constants import PROCESSED_DATASET, TARGET_COLUMN


def load_data(file_path):
    data = pd.read_csv(file_path)
    X = data.drop(TARGET_COLUMN, axis=1)
    y = data[TARGET_COLUMN]
    return X, y


def main():
    X, y = load_data(PROCESSED_DATASET)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1993)

    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)

    print("====================Test Set Metrics==================")
    print(json.dumps(metrics, indent=2))
    print("======================================================")

    save_metrics(metrics)
    plot_confusion_matrix(model, X_test, y_test)


if __name__ == "__main__":
    main()
