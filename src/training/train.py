import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
import mlflow
import mlflow.sklearn

from src.data.preprocess import preprocess_data
from src.features.build_pipeline import build_pipeline

def main():
    df = pd.DataFrame({
        "age": [25, 45, 35, 23],
        "job": ["A", "B", "A", "C"],
        "salary": [30000, 50000, 40000, 28000],
        "target": [0, 1, 1, 0]
    })

    df = preprocess_data(df)
    X = df.drop("target", axis=1)
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    pipe = build_pipeline(["job"], ["age", "salary"])

    grid = GridSearchCV(
        pipe,
        param_grid={"model__C": [0.1, 1, 10]},
        cv=3,
        scoring="f1"
    )

    with mlflow.start_run():
        grid.fit(X_train, y_train)
        mlflow.log_params(grid.best_params_)
        mlflow.sklearn.log_model(grid.best_estimator_, "model")

if __name__ == "__main__":
    main()
