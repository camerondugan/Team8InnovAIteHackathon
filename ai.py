import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score

if __name__ == "__main__":
    # Connect to the SQLite database
    conn = sqlite3.connect("testdata.db")

    # Load data from the database into a Pandas DataFrame
    query = "SELECT * FROM StudentPerformance NATURAL JOIN CourseGradeables;"
    data = pd.read_sql_query(query, conn)
    print("Data pulled:", data.columns)

    # Close the database connection
    conn.close()

    # Split data into features and target variable
    target_name = "TimeItTook"
    data["AssignmentType"] = data["AssignmentType"].astype("category")

    x = data.drop(columns=["TimeItTook", "TimeManagementFeedback", "DueDate"])
    y = data["TimeItTook"]
    print("Train Data:", x.columns)

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    # Convert data to DMatrix format for XGBoost
    dtrain = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
    dtest = xgb.DMatrix(X_test, label=y_test, enable_categorical=True)

    # Define XGBoost parameters
    params = {
        "learning_rate": 0.1,
        "eval_metric": "auc",
    }

    # Train the XGBoost model
    num_rounds = 10000
    model = xgb.train(params, dtrain, num_rounds)

    # Make predictions on the test set
    y_pred = model.predict(dtest)
    predictions = [round(value) for value in y_pred]

    # Evaluate model accuracy
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

    # Convert predictions to DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['PredictedOutcome'])

    # Add the predictions as a new column to the original DataFrame
    data['PredictedOutcome'] = predictions_df

    # Connect to the SQLite database
    conn = sqlite3.connect("testdata.db")

    # Write the DataFrame with predictions to the SQLite database
    data.to_sql('StudentPerformancePredictions', conn, if_exists='replace')

    # Close the database connection
    conn.close()
