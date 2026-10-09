
import uuid

from datetime import datetime, timezone

import pandas as pd

from django.shortcuts import render

from config.mongodb import (
    datasets_collection,
    business_records_collection,
)


BUSINESS_NUMERIC_COLUMNS = [
    "sales",
    "revenue",
    "profit",
    "cost",
    "price",
    "amount",
    "quantity",
]


BUSINESS_CATEGORICAL_COLUMNS = [
    "product",
    "category",
    "region",
    "customer",
    "customer_type",
]


def validate_dataset(df):

    errors = []

    warnings = []


    # Check empty dataset

    if df.empty:

        errors.append(
            "The dataset is empty."
        )


    # Check columns

    if len(df.columns) < 2:

        errors.append(
            "The dataset should contain at least 2 columns."
        )


    # Normalize column names

    normalized_columns = [
        column.strip().lower()
        for column in df.columns
    ]


    # Detect business numeric fields

    detected_numeric = [

        column

        for column in BUSINESS_NUMERIC_COLUMNS

        if column in normalized_columns

    ]


    # Detect business categorical fields

    detected_categorical = [

        column

        for column in BUSINESS_CATEGORICAL_COLUMNS

        if column in normalized_columns

    ]


    # Require at least one business numeric field

    if not detected_numeric:

        errors.append(
            "No business numeric column was detected. "
            "Expected columns such as sales, revenue, "
            "profit, cost, price or quantity."
        )


    # Missing values

    total_cells = (
        df.shape[0] *
        df.shape[1]
    )


    if total_cells > 0:

        missing_cells = int(
            df.isnull().sum().sum()
        )


        missing_percentage = (
            missing_cells /
            total_cells
        ) * 100


        if missing_percentage > 30:

            errors.append(
                "More than 30% of the dataset "
                "contains missing values."
            )


        elif missing_percentage > 10:

            warnings.append(
                "The dataset contains a significant "
                "number of missing values."
            )


    is_valid = len(errors) == 0


    return {

        "is_valid": is_valid,

        "errors": errors,

        "warnings": warnings,

        "detected_numeric":
            detected_numeric,

        "detected_categorical":
            detected_categorical,

    }


def convert_value(value):

    """
    Convert Pandas / NumPy values
    into MongoDB-compatible Python values.
    """

    if pd.isna(value):

        return None


    if hasattr(value, "item"):

        return value.item()


    return value


def upload_dataset(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get(
            "dataset"
        )


        # --------------------------------
        # Check file
        # --------------------------------

        if not uploaded_file:

            return render(
                request,
                "upload.html",
                {
                    "error":
                        "No file was uploaded."
                }
            )


        # --------------------------------
        # Check extension
        # --------------------------------

        if not uploaded_file.name.lower().endswith(
            ".csv"
        ):

            return render(
                request,
                "upload.html",
                {
                    "error":
                        "Invalid file type. "
                        "Please upload a CSV file."
                }
            )


        try:

            # --------------------------------
            # Read CSV
            # --------------------------------

            df = pd.read_csv(
                uploaded_file
            )


            # --------------------------------
            # Validate
            # --------------------------------

            validation = validate_dataset(
                df
            )


            rows = len(df)

            columns = len(df.columns)


            numeric_columns = (

                df.select_dtypes(
                    include="number"
                )
                .columns
                .tolist()

            )


            categorical_columns = (

                df.select_dtypes(
                    exclude="number"
                )
                .columns
                .tolist()

            )


            missing_values = int(
                df.isnull().sum().sum()
            )


            # --------------------------------
            # Save ONLY valid datasets
            # --------------------------------

            dataset_id = str(
                uuid.uuid4()
            )


            if validation["is_valid"]:

                # ----------------------------
                # Dataset metadata
                # ----------------------------

                dataset_document = {

                    "dataset_id":
                        dataset_id,

                    "filename":
                        uploaded_file.name,

                    "upload_time":
                        datetime.now(
                            timezone.utc
                        ),

                    "rows":
                        rows,

                    "columns":
                        columns,

                    "validation_status":
                        "valid",

                    "missing_values":
                        missing_values,

                    "numeric_fields":
                        numeric_columns,

                    "categorical_fields":
                        categorical_columns,

                }


                datasets_collection.insert_one(
                    dataset_document
                )


                # ----------------------------
                # Business records
                # ----------------------------

                records = []


                for row in df.to_dict(
                    orient="records"
                ):

                    clean_row = {

                        key:
                            convert_value(value)

                        for key, value
                        in row.items()

                    }


                    clean_row[
                        "dataset_id"
                    ] = dataset_id


                    records.append(
                        clean_row
                    )


                if records:

                    business_records_collection.insert_many(
                        records
                    )


            # --------------------------------
            # Result page
            # --------------------------------

            context = {

                "filename":
                    uploaded_file.name,

                "uploaded":
                    True,

                "is_valid":
                    validation["is_valid"],

                "errors":
                    validation["errors"],

                "warnings":
                    validation["warnings"],

                "rows":
                    rows,

                "columns":
                    columns,

                "missing_values":
                    missing_values,

                "numeric_columns":
                    numeric_columns,

                "categorical_columns":
                    categorical_columns,

                "detected_numeric":
                    validation[
                        "detected_numeric"
                    ],

                "detected_categorical":
                    validation[
                        "detected_categorical"
                    ],

                "dataset_id":
                    dataset_id
                    if validation["is_valid"]
                    else None,

            }


            return render(
                request,
                "upload_result.html",
                context
            )


        except Exception as e:

            return render(

                request,

                "upload.html",

                {
                    "error":
                        f"Could not process "
                        f"the file: {str(e)}"
                }

            )


    return render(
        request,
        "upload.html"
    )

def dataset_history(request):

    datasets = list(
        datasets_collection.find(
            {},
            {
                "_id": 0
            }
        ).sort(
            "upload_time",
            -1
        )
    )


    return render(
        request,
        "datasets.html",
        {
            "datasets": datasets
        }
    )


def dataset_preview(request, dataset_id):

    dataset = datasets_collection.find_one(
        {
            "dataset_id": dataset_id
        },
        {
            "_id": 0
        }
    )


    if not dataset:

        return render(
            request,
            "dataset_detail.html",
            {
                "error":
                    "Dataset not found."
            }
        )


    records = list(
        business_records_collection.find(
            {
                "dataset_id": dataset_id
            },
            {
                "_id": 0
            }
        ).limit(10)
    )


    # Get column names from the first record

    columns = []

    if records:

        columns = [
            column
            for column in records[0].keys()
            if column != "dataset_id"
        ]


    return render(
        request,
        "dataset_detail.html",
        {
            "dataset": dataset,
            "records": records,
            "columns": columns,
        }
    )


