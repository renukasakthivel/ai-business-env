from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    """Specification of an Environment Task"""
    task_id: str
    difficulty: str
    question: str
    expected_sql: str
    keywords: List[str]
    hints: List[str]

def get_tasks() -> List[Task]:
    """Provides a list of tasks scaling from Easy to Very Hard."""
    return [
        Task(
            task_id="task_1",
            difficulty="easy",
            question="Count the total number of sales transactions.",
            expected_sql="SELECT COUNT(*) FROM sales;",
            keywords=["COUNT", "sales"],
            hints=["Use the COUNT() function on the sales table."]
        ),
        Task(
            task_id="task_2",
            difficulty="medium",
            question="Find the total revenue (amount) per product category.",
            expected_sql="SELECT category, SUM(amount) FROM sales GROUP BY category;",
            keywords=["SUM", "GROUP BY", "category", "amount", "sales"],
            hints=["You need to group by category and sum the transaction amounts."]
        ),
        Task(
            task_id="task_3",
            difficulty="hard",
            question="Find the names of products that have generated more than 1000 in total revenue.",
            expected_sql="SELECT p.name FROM products p JOIN sales s ON p.product_id = s.product_id GROUP BY p.name HAVING SUM(s.amount) > 1000;",
            keywords=["JOIN", "GROUP BY", "HAVING", "SUM", "1000"],
            hints=["You have to use a JOIN on products and sales, group by the product name, and filter the grouped sum using HAVING."]
        ),
    Task(
            task_id="task_4",
            difficulty="very hard",
            question="Identify the product that has the highest average discount applied and recommend a pricing strategy.",
            expected_sql="SELECT p.name, AVG(s.discount) as avg_discount FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.name ORDER BY avg_discount DESC LIMIT 1;",
            keywords=["JOIN", "GROUP BY", "ORDER BY", "AVG", "DESC", "LIMIT"],
            hints=["Join sales and products, calculate average discount per product, sort descending, and return the top product. Also include a recommendation."]
        )
    ]
