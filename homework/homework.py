# flake8: noqa: E501
#
# En este dataset se desea pronosticar el default (pago) del cliente el próximo
# mes a partir de 23 variables explicativas.
#
#   LIMIT_BAL: Monto del credito otorgado. Incluye el credito individual y el
#              credito familiar (suplementario).
#         SEX: Genero (1=male; 2=female).
#   EDUCATION: Educacion (0=N/A; 1=graduate school; 2=university; 3=high school; 4=others).
#    MARRIAGE: Estado civil (0=N/A; 1=married; 2=single; 3=others).
#         AGE: Edad (years).
#       PAY_0: Historia de pagos pasados. Estado del pago en septiembre, 2005.
#       PAY_2: Historia de pagos pasados. Estado del pago en agosto, 2005.
#       PAY_3: Historia de pagos pasados. Estado del pago en julio, 2005.
#       PAY_4: Historia de pagos pasados. Estado del pago en junio, 2005.
#       PAY_5: Historia de pagos pasados. Estado del pago en mayo, 2005.
#       PAY_6: Historia de pagos pasados. Estado del pago en abril, 2005.
#   BILL_AMT1: Historia de pagos pasados. Monto a pagar en septiembre, 2005.
#   BILL_AMT2: Historia de pagos pasados. Monto a pagar en agosto, 2005.
#   BILL_AMT3: Historia de pagos pasados. Monto a pagar en julio, 2005.
#   BILL_AMT4: Historia de pagos pasados. Monto a pagar en junio, 2005.
#   BILL_AMT5: Historia de pagos pasados. Monto a pagar en mayo, 2005.
#   BILL_AMT6: Historia de pagos pasados. Monto a pagar en abril, 2005.
#    PAY_AMT1: Historia de pagos pasados. Monto pagado en septiembre, 2005.
#    PAY_AMT2: Historia de pagos pasados. Monto pagado en agosto, 2005.
#    PAY_AMT3: Historia de pagos pasados. Monto pagado en julio, 2005.
#    PAY_AMT4: Historia de pagos pasados. Monto pagado en junio, 2005.
#    PAY_AMT5: Historia de pagos pasados. Monto pagado en mayo, 2005.
#    PAY_AMT6: Historia de pagos pasados. Monto pagado en abril, 2005.
#
# La variable "default payment next month" corresponde a la variable objetivo.
#
# El dataset ya se encuentra dividido en conjuntos de entrenamiento y prueba
# en la carpeta "files/input/".
#
# Los pasos que debe seguir para la construcción de un modelo de
# clasificación están descritos a continuación.
#
#
# Paso 1.
# Realice la limpieza de los datasets:
# - Renombre la columna "default payment next month" a "default".
# - Remueva la columna "ID".
# - Elimine los registros con informacion no disponible.
# - Para la columna EDUCATION, valores > 4 indican niveles superiores
#   de educación, agrupe estos valores en la categoría "others".
# - Renombre la columna "default payment next month" a "default"
# - Remueva la columna "ID".
#
#
# Paso 2.
# Divida los datasets en x_train, y_train, x_test, y_test.
#
#
# Paso 3.
# Cree un pipeline para el modelo de clasificación. Este pipeline debe
# contener las siguientes capas:
# - Transforma las variables categoricas usando el método
#   one-hot-encoding.
# - Ajusta un modelo de bosques aleatorios (rando forest).
#
#
# Paso 4.
# Optimice los hiperparametros del pipeline usando validación cruzada.
# Use 10 splits para la validación cruzada. Use la función de precision
# balanceada para medir la precisión del modelo.
#
#
# Paso 5.
# Guarde el modelo (comprimido con gzip) como "files/models/model.pkl.gz".
# Recuerde que es posible guardar el modelo comprimido usanzo la libreria gzip.
#
#
# Paso 6.
# Calcule las metricas de precision, precision balanceada, recall,
# y f1-score para los conjuntos de entrenamiento y prueba.
# Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# Este diccionario tiene un campo para indicar si es el conjunto
# de entrenamiento o prueba. Por ejemplo:
#
# {'dataset': 'train', 'precision': 0.8, 'balanced_accuracy': 0.7, 'recall': 0.9, 'f1_score': 0.85}
# {'dataset': 'test', 'precision': 0.7, 'balanced_accuracy': 0.6, 'recall': 0.8, 'f1_score': 0.75}
#
#
# Paso 7.
# Calcule las matrices de confusion para los conjuntos de entrenamiento y
# prueba. Guardelas en el archivo files/output/metrics.json. Cada fila
# del archivo es un diccionario con las metricas de un modelo.
# de entrenamiento o prueba. Por ejemplo:
#
# {'type': 'cm_matrix', 'dataset': 'train', 'true_0': {"predicted_0": 15562, "predicte_1": 666}, 'true_1': {"predicted_0": 3333, "predicted_1": 1444}}
# {'type': 'cm_matrix', 'dataset': 'test', 'true_0': {"predicted_0": 15562, "predicte_1": 650}, 'true_1': {"predicted_0": 2490, "predicted_1": 1420}}
#


import pandas as pd #type: ignore
import os #type: ignore
import gzip #type: ignore
import pickle #type: ignore
import json #type: ignore
from sklearn.model_selection import GridSearchCV #type: ignore
from sklearn.ensemble import RandomForestClassifier#type: ignore
from sklearn.pipeline import Pipeline #type: ignore
from sklearn.compose import ColumnTransformer 
from sklearn.preprocessing import OneHotEncoder #type: ignore
from sklearn.metrics import precision_score, balanced_accuracy_score, recall_score, f1_score, confusion_matrix #type: ignore

#Se carga la data desde un archivo comprimido en formato zip
def cargar_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, index_col=False, compression="zip")

#Preprocesamiento inicial de los datos
def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"default payment next month": "default"})
    df = df.drop(columns=["ID"])
    df = df.loc[df["MARRIAGE"] != 0] 
    df = df.loc[df["EDUCATION"] != 0] 
    df["EDUCATION"] = df["EDUCATION"].apply(lambda x: x if x < 4 else 4)
    return df

#Creación de la pipeline de procesamiento y clasificación
def crear_pipeline() -> Pipeline:
    cat_features = ["SEX", "EDUCATION", "MARRIAGE"]
    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)],
        remainder="passthrough",
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(random_state=42)),
        ]
    )

#Creación del estimador con GridSearchCV para optimizar hiperparámetros
def crear_estimador(pipeline: Pipeline) -> GridSearchCV:
    param_grid = {
        "classifier__n_estimators": [50, 100, 200],
        "classifier__max_depth": [None, 5, 10, 20],
        "classifier__min_samples_split": [2, 5, 10],
        "classifier__min_samples_leaf": [1, 2, 4],
    }

    return GridSearchCV(
        pipeline,
        param_grid,
        cv=10,
        scoring="balanced_accuracy",
        n_jobs=-1,
        verbose=2,
        refit=True,
    )

# Guardar el modelo entrenado en un archivo comprimido
def guardar_model(path: str, estimator: GridSearchCV):
    os.makedirs(os.path.dirname(path), exist_ok=True) 
    with gzip.open(path, "wb") as f:
        pickle.dump(estimator, f)

# Calcular métricas de precisión y otras métricas de evaluación
def metrics(dataset_name: str, y_true, y_pred) -> dict:
    return {
        "type": "metrics",
        "dataset": dataset_name,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
    }

# Calcular la matriz de confusión y sus métricas asociadas
def calculate_confusion_metrics(dataset_name: str, y_true, y_pred) -> dict:
    cm = confusion_matrix(y_true, y_pred)
    return {
        "type": "cm_matrix",
        "dataset": dataset_name,
        "true_0": {"predicted_0": int(cm[0][0]), "predicted_1": int(cm[0][1])},
        "true_1": {"predicted_0": int(cm[1][0]), "predicted_1": int(cm[1][1])},
    }

# Función main que ejecuta todo el flujo de trabajo
def main():
    input_files_path = "files/input/"
    models_files_path = "files/models/"
    output_files_path = "files/output/"

    #Carga data
    test_df = cargar_data(os.path.join(input_files_path, "test_data.csv.zip"))
    train_df = cargar_data(os.path.join(input_files_path, "train_data.csv.zip"))
    #Limpieza de data
    test_df = clean_dataset(test_df)
    train_df = clean_dataset(train_df)
    #Dropea columnas y separa en x e y
    x_test = test_df.drop(columns=["default"])
    y_test = test_df["default"]
    #Separa el conjunto de entrenamiento en x e y
    x_train = train_df.drop(columns=["default"])
    y_train = train_df["default"]
    #Crea la pipeline y el estimador
    pipeline = crear_pipeline()
    #Crea el estimador con GridSearchCV
    estimator = crear_estimador(pipeline)
    estimator.fit(x_train, y_train)
    #Guarda el modelo entrenado
    guardar_model(os.path.join(models_files_path, "model.pkl.gz"), estimator)
    #Realiza predicciones y calcula métricas
    y_test_pred = estimator.predict(x_test)
    test_precision_metrics = metrics("test", y_test, y_test_pred)
    y_train_pred = estimator.predict(x_train)
    train_precision_metrics = metrics("train", y_train, y_train_pred)
    #Calcula las métricas de confusión
    test_confusion_metrics = calculate_confusion_metrics("test", y_test, y_test_pred)
    train_confusion_metrics = calculate_confusion_metrics("train", y_train, y_train_pred)
    #Guarda las métricas en un archivo JSON
    os.makedirs(output_files_path, exist_ok=True)
    with open(os.path.join(output_files_path, "metrics.json"), "w") as file:
        file.write(json.dumps(train_precision_metrics) + "\n")
        file.write(json.dumps(test_precision_metrics) + "\n")
        file.write(json.dumps(train_confusion_metrics) + "\n")
        file.write(json.dumps(test_confusion_metrics) + "\n")

if __name__ == "__main__":
    main()
