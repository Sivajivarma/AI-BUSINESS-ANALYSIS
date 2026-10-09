
from analytics.llm_service import generate_business_answer


context = """
BUSINESS METRICS — calculated from the dataset:

Total sales: Rs. 1,795,000
Total profit: Rs. 391,000
Overall profit margin: 21.78%

PRODUCT SALES — ranked highest to lowest:
1. Phone: Rs. 780,000 (43.45% of total sales)
2. Laptop: Rs. 600,000 (33.43% of total sales)
3. Tablet: Rs. 280,000 (15.60% of total sales)
4. Headphones: Rs. 135,000 (7.52% of total sales)

REGIONAL SALES — ranked highest to lowest:
1. South: Rs. 695,000
2. North: Rs. 500,000
3. East: Rs. 420,000
4. West: Rs. 180,000

IMPORTANT:
- Phone has the highest sales.
- South is the highest-selling region.
- The overall profit margin does not establish
  the profit margin of any individual product.
- Product-level profit margins were not provided.
- Do not invent additional numbers.
- Recommend Phone as the product to investigate
  for further investment, but explain that sales
  alone do not prove it has the highest profitability.
"""

question = "Which product should the business focus on?"

answer = generate_business_answer(
    question,
    context,
)

print("\n===== AI BUSINESS ANALYST =====\n")
print(answer)