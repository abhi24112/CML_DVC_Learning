import json

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay


def plot_confusion_matrix(model, X_test, y_test):
    _ = ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, cmap=plt.cm.Blues)
    plt.savefig("confusion_matrix.png")


def save_metrics(metrics):
    with open("metrics.json", "w") as fp:
        json.dump(metrics, fp)
