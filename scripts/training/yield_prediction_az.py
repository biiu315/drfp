import pickle
from pathlib import Path
from typing import Tuple
from statistics import stdev
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error


def save_results(
    set_name: str,
    split_id: str,
    file_name: str,
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> None:
    with open(f"{set_name}_{split_id}_{file_name}.csv", "w+") as f:
        for gt, pred in zip(ground_truth, prediction):
            f.write(f"{set_name},{split_id},{file_name},{gt},{pred}\n")


def predict_az():
    root_path = Path(__file__).resolve().parent
    az_file_path = Path(root_path, "../../data/az/az-2048-3-true.pkl")

    data = pickle.load(open(az_file_path, "rb"))

    r2s = []
    maes = []

    for i, split in enumerate(data):
        X_train, y_train, X_valid, y_valid, X_test, y_test = (
            split["train"]["X"],
            split["train"]["y"],
            split["valid"]["X"],
            split["valid"]["y"],
            split["test"]["X"],
            split["test"]["y"],
        )

        # Vanilla hyperparams
        model = XGBRegressor(
            n_estimators=999999,
            learning_rate=0.01,
            max_depth=12,
            min_child_weight=6,
            colsample_bytree=0.6,
            subsample=0.8,
            random_state=42,
        )

        model.fit(
            X_train,
            y_train,
            eval_set=[(X_valid, y_valid)],
            early_stopping_rounds=10,
            verbose=False,
        )

        y_pred = model.predict(X_test, ntree_limit=model.best_ntree_limit)
        y_pred[y_pred < 0.0] = 0.0

        # save_results("az", split, sample_file, y_test, y_pred)
        r_squared = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        print(f"Test {i + 1}", r_squared, mae)
        r2s.append(r_squared)
        maes.append(mae)

    print("Tests R2:", sum(r2s) / len(r2s), stdev(r2s))
    print("Tests MAE:", sum(maes) / len(maes), stdev(maes))


def main():
    predict_az()


if __name__ == "__main__":
    main()
