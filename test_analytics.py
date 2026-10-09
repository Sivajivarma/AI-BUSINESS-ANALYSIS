
from analytics.engine import calculate_analytics


dataset_id = input(
    "Enter Dataset ID: "
)


result = calculate_analytics(
    dataset_id
)


print("\n")
print("===== ANALYTICS RESULT =====")
print("\n")


if not result["success"]:

    print(
        "Error:",
        result["error"]
    )

else:

    print(
        "Rows Analyzed:",
        result["rows_analyzed"]
    )

    print(
        "Total Sales:",
        result["total_sales"]
    )

    print(
        "Total Profit:",
        result["total_profit"]
    )

    print(
        "Total Quantity:",
        result["total_quantity"]
    )

    print(
        "Average Sale:",
        result["average_sale"]
    )

    print(
        "Profit Margin:",
        result["profit_margin"],
        "%"
    )

    print(
        "Top Product:",
        result["top_product"]
    )

    print(
        "Top Region:",
        result["top_region"]
    )

    print(
        "Unique Products:",
        result["unique_products"]
    )

    print(
        "Unique Regions:",
        result["unique_regions"]
    )
