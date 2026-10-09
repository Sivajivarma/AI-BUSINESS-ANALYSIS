from django.shortcuts import render

from .engine import calculate_analytics
from .analyst import ask_llm_business_analyst

def analytics_dashboard(request, dataset_id):
    result = calculate_analytics(dataset_id)

    return render(
        request,
        "analytics_dashboard.html",
        {
            "result": result,
            "dataset_id": dataset_id,
        }
    )

def ai_business_analyst(request, dataset_id):
    answer = None
    question = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if question:
            answer = ask_llm_business_analyst(
                dataset_id,
                question
            )

    return render(
        request,
        "ai_analyst.html",
        {
            "dataset_id": dataset_id,
            "answer": answer,
            "question": question,
        }
    )