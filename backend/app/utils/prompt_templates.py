"""
AI prompt templates for financial coaching.
These templates provide context to Gemini for generating relevant responses.
"""

SYSTEM_PROMPT = """You are an expert AI Financial Coach for the Finance Dashboard app.

Your role:
- Analyze user spending patterns and provide actionable insights
- Answer questions about personal finance clearly and concisely
- Suggest practical ways to save money and improve financial health
- Be encouraging and supportive, not judgmental
- Use emojis sparingly for emphasis (1-2 per response max)

Guidelines:
- Keep responses under 200 words unless detailed analysis is requested
- Always cite specific numbers from the user's data when available
- Provide 2-3 concrete suggestions rather than generic advice
- If data is insufficient, ask clarifying questions
- Never recommend risky investments or financial products

Response Format:
- Start with a direct answer to the question
- Provide supporting data/evidence
- End with 1-2 actionable suggestions
- Format responses in plain text without bold (**) or other markdown

Example:
  User: "What are my biggest expenses?"
  Good Response:
  Your Bills & Utilities category is your largest expense at $4000.00, making up 54.1% of your total spending. Transportation comes second at $2000.00 (27%). Here are 
  some ways to reduce these:
  1. Review your utility bills for any services you're not using
  2. Consider carpooling or public transport to reduce transportation costs

  Bad Response:
  Your **Bills & Utilities** category is your **largest expense** at **$4000.00**...
"""

def create_user_context_prompt(
    user_data: dict,
    transactions: list,
    question: str
) -> str:
    """
    Creates a comprehensive prompt with user context.

    Args:
        user_data: Dict with user info (income, name, etc.)
        transactions: List of recent transactions
        question: User's question

    Returns:
        Formatted prompt string
    """

    # Calculate summary statistics
    total_spent = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')

    # Category breakdown
    category_spending = {}
    for t in transactions:
        if t['type'] == 'expense':
            cat = t.get('category', 'Other')
            category_spending[cat] = category_spending.get(cat, 0) + t['amount']

    # Format transactions for context (last 10)
    recent_transactions = "\n".join([
        f"- {t['date']}: {t['description']} - ${t['amount']:.2f} ({t.get('category', 'N/A')})"
        for t in transactions[-10:]
    ])

    # Format category spending
    category_breakdown = "\n".join([
        f"- {cat}: ${amt:.2f} ({(amt/total_spent*100):.1f}%)"
        for cat, amt in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
    ]) if total_spent > 0 else "No expenses recorded"

    prompt = f"""
                USER FINANCIAL CONTEXT:
                ====================
                Name: {user_data.get('name', 'User')}
                Monthly Income: ${user_data.get('income', 0):.2f}

                CURRENT PERIOD SUMMARY:
                - Total Spent: ${total_spent:.2f}
                - Total Income: ${total_income:.2f}
                - Net: ${total_income - total_spent:.2f}

                SPENDING BY CATEGORY:
                {category_breakdown}

                RECENT TRANSACTIONS (Last 10):
                {recent_transactions if recent_transactions else "No transactions"}

                USER QUESTION:
                {question}

                Please provide a helpful, data-driven response based on the above context.
              """

    return prompt


QUICK_QUESTIONS = [
    "Why is my spending high this month?",
    "How can I save more money?",
    "What's my biggest expense category?",
    "Am I on track with my budget?",
    "Give me 3 ways to reduce spending",
    "Analyze my spending patterns"
]


def create_budget_analysis_prompt(
    income: float,
    total_spending: float,
    category_breakdown: dict
) -> str:
    """Generate prompt for budget analysis."""

    categories_text = "\n".join([
        f"- {cat}: ${amt:.2f} ({(amt/total_spending*100):.1f}%)"
        for cat, amt in category_breakdown.items()
    ]) if total_spending > 0 else "No expenses recorded"

    savings_rate = ((income - total_spending) / income * 100) if income > 0 else 0

    return f"""
Analyze this budget and provide recommendations:

Monthly Income: ${income:.2f}
Total Spending: ${total_spending:.2f}
Savings Rate: {savings_rate:.1f}%

Category Breakdown:
{categories_text}

Provide:
1. Overall assessment (good/concerning/needs improvement)
2. Apply the 50/30/20 rule and compare with actual spending
3. Top 2-3 specific recommendations to improve financial health
"""
