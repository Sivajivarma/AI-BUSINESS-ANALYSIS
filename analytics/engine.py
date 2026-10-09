import json
import pandas as pd

from config.mongodb import business_records_collection

def generate_recommendations(
    df,
    total_sales,
    total_profit,
    profit_margin,
    top_product,
    top_region
):
    recommendations = []

    # Product recommendation
    if (
        top_product
        and "product" in df.columns
        and "sales" in df.columns
    ):
        product_sales = (
            df.groupby("product")["sales"]
            .sum()
            .sort_values(ascending=False)
        )

        if len(product_sales) > 1:
            highest_sales = product_sales.iloc[0]
            lowest_sales = product_sales.iloc[-1]

            highest_product = product_sales.index[0]
            lowest_product = product_sales.index[-1]

            recommendations.append(
                f"Focus marketing and inventory on {highest_product}, "
                f"which generates the highest sales."
            )

            recommendations.append(
                f"Review the performance of {lowest_product}, "
                f"which has the lowest sales among the products."
            )

    # Regional recommendation
    if (
        top_region
        and "region" in df.columns
        and "sales" in df.columns
    ):
        recommendations.append(
            f"{top_region} is the strongest region. "
            f"Consider expanding successful strategies in this region."
        )

    # Profit recommendation
    if profit_margin >= 30:
        recommendations.append(
            f"Profit margin is strong at {profit_margin:.2f}%. "
            f"Consider scaling the business while maintaining current margins."
        )

    elif profit_margin >= 15:
        recommendations.append(
            f"Profit margin is moderate at {profit_margin:.2f}%. "
            f"Review costs and pricing to improve profitability."
        )

    else:
        recommendations.append(
            f"Profit margin is low at {profit_margin:.2f}%. "
            f"Investigate operating costs, pricing, and low-margin products."
        )

    # Sales availability
    if total_sales == 0:
        recommendations.append(
            "No sales data was detected. Review the dataset before making business decisions."
        )

    # Profit availability
    if total_profit <= 0:
        recommendations.append(
            "The dataset shows little or no positive profit. "
            "Investigate high-cost products and pricing."
        )

    return recommendations

def get_dataset_records(dataset_id):

    records = list(
        business_records_collection.find(
            {
                "dataset_id": dataset_id
            },
            {
                "_id": 0
            }
        )
    )

    return records


def calculate_analytics(dataset_id):

    records = get_dataset_records(dataset_id)

    if not records:

        return {
            "success": False,
            "error": "No records found for this dataset."
        }


    df = pd.DataFrame(records)


    if "dataset_id" in df.columns:

        df = df.drop(columns=["dataset_id"])


    # --------------------------------
    # BASIC COLUMN INFORMATION
    # --------------------------------

    numeric_columns = (
        df.select_dtypes(include="number")
        .columns
        .tolist()
    )

    categorical_columns = (
        df.select_dtypes(exclude="number")
        .columns
        .tolist()
    )


    # --------------------------------
    # BASIC KPIs
    # --------------------------------

    total_sales = 0

    if "sales" in df.columns:

        total_sales = float(
            df["sales"].sum()
        )

    elif "revenue" in df.columns:

        total_sales = float(
            df["revenue"].sum()
        )


    total_profit = 0

    if "profit" in df.columns:

        total_profit = float(
            df["profit"].sum()
        )


    total_quantity = 0

    if "quantity" in df.columns:

        total_quantity = float(
            df["quantity"].sum()
        )


    average_sale = 0

    if total_sales > 0:

        average_sale = (
            total_sales / len(df)
        )


    profit_margin = 0

    if total_sales > 0:

        profit_margin = (
            total_profit / total_sales
        ) * 100


    # --------------------------------
    # PRODUCT ANALYSIS
    # --------------------------------

    top_product = None

    product_labels = []

    product_values = []

    product_profit_values = []


    if (
        "product" in df.columns
        and "sales" in df.columns
    ):

        product_sales = (

            df.groupby("product")["sales"]

            .sum()

            .sort_values(
                ascending=False
            )
        )


        product_labels = (
            product_sales.index.tolist()
        )


        product_values = (
            product_sales.tolist()
        )


        if not product_sales.empty:

            top_product = (
                product_sales.index[0]
            )


    if (
        "product" in df.columns
        and "profit" in df.columns
    ):

        product_profit = (

            df.groupby("product")["profit"]

            .sum()

            .reindex(product_labels)

            .fillna(0)
        )


        product_profit_values = (
            product_profit.tolist()
        )


    # --------------------------------
    # REGION ANALYSIS
    # --------------------------------

    top_region = None

    region_labels = []

    region_values = []


    if (
        "region" in df.columns
        and "sales" in df.columns
    ):

        region_sales = (

            df.groupby("region")["sales"]

            .sum()

            .sort_values(
                ascending=False
            )
        )


        region_labels = (
            region_sales.index.tolist()
        )


        region_values = (
            region_sales.tolist()
        )


        if not region_sales.empty:

            top_region = (
                region_sales.index[0]
            )


    # --------------------------------
    # UNIQUE VALUES
    # --------------------------------

    unique_products = 0

    if "product" in df.columns:

        unique_products = int(
            df["product"].nunique()
        )


    unique_regions = 0

    if "region" in df.columns:

        unique_regions = int(
            df["region"].nunique()
        )


    # --------------------------------
    # DATE ANALYSIS
    # --------------------------------

    date_labels = []

    date_sales_values = []

    date_profit_values = []


    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )


        date_df = df.dropna(
            subset=["date"]
        )


        if not date_df.empty:

            if "sales" in date_df.columns:

                daily_sales = (

                    date_df
                    .groupby("date")["sales"]
                    .sum()
                    .sort_index()
                )


                date_labels = [

                    date.strftime("%Y-%m-%d")

                    for date in daily_sales.index
                ]


                date_sales_values = (
                    daily_sales.tolist()
                )


            if "profit" in date_df.columns:

                daily_profit = (

                    date_df
                    .groupby("date")["profit"]
                    .sum()
                    .sort_index()
                )


                date_profit_values = (
                    daily_profit.tolist()
                )


    # --------------------------------
    # LOW PERFORMING PRODUCTS
    # --------------------------------

    low_performing_products = []


    if (
        "product" in df.columns
        and "sales" in df.columns
    ):

        product_sales = (

            df.groupby("product")["sales"]

            .sum()

            .sort_values()
        )


        if len(product_sales) > 1:

            low_product_count = max(
                1,
                int(len(product_sales) * 0.25)
            )


            low_performing_products = (

                product_sales
                .head(low_product_count)
                .index
                .tolist()
            )


    # --------------------------------
    # AUTOMATIC BUSINESS INSIGHTS
    # --------------------------------

    insights = []


    if top_product:

        insights.append(
            f"{top_product} is the highest-selling product."
        )


    if top_region:

        insights.append(
            f"{top_region} is the strongest-performing region."
        )


    if profit_margin > 30:

        insights.append(
            f"Overall profit margin is strong at {profit_margin:.2f}%."
        )

    elif profit_margin > 15:

        insights.append(
            f"Overall profit margin is moderate at {profit_margin:.2f}%."
        )

    else:

        insights.append(
            f"Profit margin is relatively low at {profit_margin:.2f}%."
        )


    for product in low_performing_products:

        insights.append(
            f"{product} is among the lowest-performing products by sales."
        )

        recommendations = generate_recommendations(
        df,
        total_sales,
        total_profit,
        profit_margin,
        top_product,
        top_region
        )


    # --------------------------------
    # CONVERT TO JSON
    # --------------------------------

    product_labels_json = json.dumps(
        product_labels
    )

    product_values_json = json.dumps(
        product_values
    )

    product_profit_values_json = json.dumps(
        product_profit_values
    )

    region_labels_json = json.dumps(
        region_labels
    )

    region_values_json = json.dumps(
        region_values
    )

    date_labels_json = json.dumps(
        date_labels
    )

    date_sales_values_json = json.dumps(
        date_sales_values
    )

    date_profit_values_json = json.dumps(
        date_profit_values
    )


    # --------------------------------
    # FINAL RESULT
    # --------------------------------

    return {

        "success": True,

        "rows_analyzed": len(df),

        "numeric_columns": numeric_columns,

        "categorical_columns": categorical_columns,

        "total_sales": total_sales,

        "total_profit": total_profit,

        "total_quantity": total_quantity,

        "average_sale": average_sale,

        "profit_margin": profit_margin,

        "top_product": top_product,

        "top_region": top_region,

        "unique_products": unique_products,

        "unique_regions": unique_regions,

        "product_labels": product_labels_json,

        "product_values": product_values_json,

        "product_profit_values": product_profit_values_json,

        "region_labels": region_labels_json,

        "region_values": region_values_json,

        "date_labels": date_labels_json,

        "date_sales_values": date_sales_values_json,

        "date_profit_values": date_profit_values_json,

        "low_performing_products": low_performing_products,

        "insights": insights,
        "recommendations": recommendations,
    }