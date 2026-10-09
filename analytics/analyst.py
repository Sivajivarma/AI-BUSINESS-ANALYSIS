import pandas as pd

from config.mongodb import business_records_collection
from .llm_service import generate_business_answer

def get_records(dataset_id):
    records = list(
        business_records_collection.find(
            {"dataset_id": dataset_id},
            {"_id": 0}
        )
    )

    return records


def get_sales_column(df):
    if "sales" in df.columns:
        return "sales"

    if "revenue" in df.columns:
        return "revenue"

    return None


def answer_business_question(dataset_id, question):

    records = get_records(dataset_id)

    if not records:
        return {
            "success": False,
            "answer": "No data was found for this dataset."
        }

    df = pd.DataFrame(records)

    if "dataset_id" in df.columns:
        df = df.drop(columns=["dataset_id"])

    question = question.lower().strip()

    sales_column = get_sales_column(df)

    if not sales_column:
        return {
            "success": False,
            "answer": (
                "I cannot answer business sales questions because "
                "the dataset does not contain a sales or revenue column."
            )
        }

    # --------------------------------------------------
    # PRODUCT ANALYSIS
    # --------------------------------------------------

    if "product" in df.columns:

        product_sales = (
            df.groupby("product")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )

    else:
        product_sales = None


    # --------------------------------------------------
    # REGION ANALYSIS
    # --------------------------------------------------

    if "region" in df.columns:

        region_sales = (
            df.groupby("region")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )

    else:
        region_sales = None


    # --------------------------------------------------
    # BEST PRODUCT
    # --------------------------------------------------

    if (
        product_sales is not None
        and (
            "best product" in question
            or "top product" in question
            or "highest selling" in question
            or "best performing product" in question
        )
    ):

        product = product_sales.index[0]

        sales = product_sales.iloc[0]

        return {
            "success": True,

            "answer": (
                f"{product} is the best-performing product "
                f"based on sales. It generated "
                f"₹{sales:,.0f} in sales."
            ),

            "metric_title": "Top Product",

            "metric_value": product,

            "supporting_text": (
                f"Sales generated: ₹{sales:,.0f}"
            )
        }


    # --------------------------------------------------
    # INVESTMENT QUESTION
    # --------------------------------------------------

    if (
        product_sales is not None
        and (
            "invest" in question
            or "focus on" in question
            or "promote" in question
        )
    ):

        product = product_sales.index[0]

        sales = product_sales.iloc[0]

        total_sales = product_sales.sum()

        contribution = (
            sales / total_sales * 100
        )

        return {
            "success": True,

            "answer": (
                f"{product} is the strongest candidate "
                f"for additional investment because it "
                f"generated the highest sales of "
                f"₹{sales:,.0f}."
            ),

            "metric_title": "Recommended Product",

            "metric_value": product,

            "supporting_text": (
                f"{contribution:.1f}% of total product sales"
            )
        }


    # --------------------------------------------------
    # REGION QUESTION
    # --------------------------------------------------

    if (
        region_sales is not None
        and (
            "best region" in question
            or "top region" in question
            or "strongest region" in question
            or "region is performing" in question
        )
    ):

        region = region_sales.index[0]

        sales = region_sales.iloc[0]

        return {
            "success": True,

            "answer": (
                f"{region} is the strongest-performing region. "
                f"It generated ₹{sales:,.0f} in sales."
            ),

            "metric_title": "Top Region",

            "metric_value": region,

            "supporting_text": (
                f"Regional sales: ₹{sales:,.0f}"
            )
        }


    # --------------------------------------------------
    # WEAK PRODUCT
    # --------------------------------------------------

    if (
        product_sales is not None
        and (
            "weakest" in question
            or "lowest" in question
            or "poor performing" in question
            or "poorly" in question
        )
    ):

        product = product_sales.index[-1]

        sales = product_sales.iloc[-1]

        return {
            "success": True,

            "answer": (
                f"{product} is currently the weakest product "
                f"based on sales, generating only "
                f"₹{sales:,.0f}."
            ),

            "metric_title": "Weakest Product",

            "metric_value": product,

            "supporting_text": (
                f"Sales generated: ₹{sales:,.0f}"
            )
        }


    # --------------------------------------------------
    # PROFIT QUESTION
    # --------------------------------------------------

    if (
        "profit" in question
        or "margin" in question
    ):

        if "profit" not in df.columns:

            return {
                "success": False,
                "answer": (
                    "This dataset does not contain a profit column."
                )
            }

        total_sales = df[sales_column].sum()

        total_profit = df["profit"].sum()

        margin = 0

        if total_sales > 0:
            margin = (
                total_profit / total_sales
            ) * 100

        return {
            "success": True,

            "answer": (
                f"The business generated "
                f"₹{total_profit:,.0f} in total profit "
                f"with a profit margin of "
                f"{margin:.2f}%."
            ),

            "metric_title": "Profit Margin",

            "metric_value": f"{margin:.2f}%",

            "supporting_text": (
                f"Total profit: ₹{total_profit:,.0f}"
            )
        }


    # --------------------------------------------------
    # SALES DECREASE QUESTION
    # --------------------------------------------------

    if (
        "decrease" in question
        or "decline" in question
        or "declining" in question
        or "fall" in question
        or "dropping" in question
    ):

        if "date" not in df.columns:

            return {
                "success": False,
                "answer": (
                    "I need a date column to analyze "
                    "sales trends and determine whether "
                    "sales are decreasing."
                )
            }

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        trend_df = df.dropna(subset=["date"])

        if len(trend_df) < 2:

            return {
                "success": False,
                "answer": (
                    "There is not enough dated data "
                    "to analyze the sales trend."
                )
            }

        trend_df = trend_df.sort_values("date")

        midpoint = len(trend_df) // 2

        first_half = trend_df.iloc[:midpoint]

        second_half = trend_df.iloc[midpoint:]

        first_sales = first_half[sales_column].sum()

        second_sales = second_half[sales_column].sum()

        if first_sales > 0:

            change = (
                (second_sales - first_sales)
                / first_sales
            ) * 100

        else:
            change = 0

        if change < 0:

            answer = (
                f"Sales decreased by "
                f"{abs(change):.2f}% when comparing "
                f"the later period with the earlier period. "
                f"Earlier sales were ₹{first_sales:,.0f}, "
                f"while later sales were ₹{second_sales:,.0f}."
            )

        else:

            answer = (
                f"Sales did not decrease in the available "
                f"period. Sales changed by "
                f"{change:.2f}% between the earlier "
                f"and later periods."
            )

        return {
            "success": True,

            "answer": answer,

            "metric_title": "Sales Change",

            "metric_value": f"{change:.2f}%",

            "supporting_text": (
                f"Earlier: ₹{first_sales:,.0f} | "
                f"Later: ₹{second_sales:,.0f}"
            )
        }


    # --------------------------------------------------
    # GENERAL BUSINESS QUESTION
    # --------------------------------------------------

    total_sales = df[sales_column].sum()

    answer = (
        f"The dataset contains {len(df)} business records "
        f"with total sales of ₹{total_sales:,.0f}. "
    )

    if product_sales is not None:

        top_product = product_sales.index[0]

        answer += (
            f"The highest-selling product is "
            f"{top_product}. "
        )

    if region_sales is not None:

        top_region = region_sales.index[0]

        answer += (
            f"The strongest region is "
            f"{top_region}."
        )

    return {
        "success": True,

        "answer": answer,

        "metric_title": "Total Sales",

        "metric_value": f"₹{total_sales:,.0f}",

        "supporting_text": "Based on the uploaded dataset"
    }

def build_business_context(dataset_id):

    records = get_records(dataset_id)

    if not records:
        return None

    df = pd.DataFrame(records)

    if "dataset_id" in df.columns:
        df = df.drop(columns=["dataset_id"])


    context = []


    # Dataset information

    context.append(
        f"Total records: {len(df)}"
    )


    # Sales

    sales_column = get_sales_column(df)

    if sales_column:

        total_sales = df[sales_column].sum()

        context.append(
            f"Total sales: ₹{total_sales:,.2f}"
        )


    # Profit

    if "profit" in df.columns:

        total_profit = df["profit"].sum()

        context.append(
            f"Total profit: ₹{total_profit:,.2f}"
        )

        if sales_column:

            total_sales = df[sales_column].sum()

            if total_sales > 0:

                margin = (
                    total_profit / total_sales
                ) * 100

                context.append(
                    f"Profit margin: {margin:.2f}%"
                )


    # Quantity

    if "quantity" in df.columns:

        total_quantity = df["quantity"].sum()

        context.append(
            f"Total quantity sold: {total_quantity:,.0f}"
        )


    # Products

    if (
        "product" in df.columns
        and sales_column
    ):

        product_sales = (
            df.groupby("product")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )


        context.append(
            "\nProduct performance:"
        )


        for product, sales in product_sales.items():

            context.append(
                f"- {product}: ₹{sales:,.2f}"
            )


    # Regions

    if (
        "region" in df.columns
        and sales_column
    ):

        region_sales = (
            df.groupby("region")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )


        context.append(
            "\nRegional performance:"
        )


        for region, sales in region_sales.items():

            context.append(
                f"- {region}: ₹{sales:,.2f}"
            )


    return "\n".join(context)
def ask_llm_business_analyst(
    dataset_id,
    question
):

    business_context = build_business_context(
        dataset_id
    )


    if not business_context:

        return {
            "success": False,

            "answer": (
                "No business data was found "
                "for this dataset."
            )
        }


    try:

        answer = generate_business_answer(
            question,
            business_context
        )


        return {
            "success": True,

            "answer": answer,

            "context": business_context
        }


    except Exception as error:

        return {
            "success": False,

            "answer": (
                "The AI Business Analyst could not "
                "process the request right now."
            ),

            "error": str(error)
        }

def build_business_context(dataset_id):
    records = get_records(dataset_id)

    if not records:
        return None

    df = pd.DataFrame(records)

    if "dataset_id" in df.columns:
        df = df.drop(columns=["dataset_id"])

    context = [f"Total records: {len(df)}"]

    sales_column = get_sales_column(df)

    if sales_column:
        total_sales = float(df[sales_column].sum())
        context.append(f"Total sales: Rs. {total_sales:,.2f}")

    if "profit" in df.columns:
        total_profit = float(df["profit"].sum())
        context.append(f"Total profit: Rs. {total_profit:,.2f}")

        if sales_column:
            total_sales = float(df[sales_column].sum())

            if total_sales > 0:
                margin = (total_profit / total_sales) * 100
                context.append(
                    f"Overall profit margin: {margin:.2f}%"
                )

    if "quantity" in df.columns:
        total_quantity = float(df["quantity"].sum())
        context.append(
            f"Total quantity sold: {total_quantity:,.0f}"
        )

    if "product" in df.columns and sales_column:
        product_sales = (
            df.groupby("product")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )

        context.append("\nProduct sales, highest to lowest:")

        for product, sales in product_sales.items():
            context.append(
                f"- {product}: Rs. {sales:,.2f}"
            )

    if "region" in df.columns and sales_column:
        region_sales = (
            df.groupby("region")[sales_column]
            .sum()
            .sort_values(ascending=False)
        )

        context.append("\nRegional sales, highest to lowest:")

        for region, sales in region_sales.items():
            context.append(
                f"- {region}: Rs. {sales:,.2f}"
            )

    context.append(
        "\nUse only the supplied metrics. "
        "Do not invent numbers or product-level margins. "
        "Sales performance does not necessarily mean "
        "profitability."
    )

    return "\n".join(context)


def ask_llm_business_analyst(dataset_id, question):
    business_context = build_business_context(dataset_id)

    if not business_context:
        return {
            "success": False,
            "answer": "No business data was found for this dataset."
        }

    try:
        answer = generate_business_answer(
            question,
            business_context
        )

        return {
            "success": True,
            "answer": answer
        }

    except Exception:
        return {
            "success": False,
            "answer": (
                "The local AI analyst could not respond. "
                "Please check that Ollama is running and "
                "the configured model is installed."
            )
        }