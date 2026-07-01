"""Command line interface for the AI Agentic Expense Assistant."""

from agent import ExpenseAgent


def print_menu():
    """Display the main menu."""
    print("\n====================================")
    print(" AI AGENTIC EXPENSE ASSISTANT")
    print("====================================")
    print("1. Ask an expense policy question")
    print("2. Check an expense claim")
    print("3. Summarize a policy")
    print("4. Run evaluation")
    print("5. Give feedback")
    print("6. Exit")
    print("====================================")


def prompt_non_empty(message):
    """Prompt until the user enters non-empty text."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def prompt_amount():
    """Prompt until the user enters a valid positive amount."""
    while True:
        raw_amount = input("Enter amount in INR: ").strip()
        try:
            amount = float(raw_amount)
        except ValueError:
            print("Amount must be numeric. Example: 900")
            continue

        if amount <= 0:
            print("Amount must be greater than zero.")
            continue

        return amount


def prompt_rating():
    """Prompt until the user enters a rating from 1 to 5."""
    while True:
        raw_rating = input("Enter rating from 1 to 5: ").strip()
        if raw_rating.isdigit() and 1 <= int(raw_rating) <= 5:
            return int(raw_rating)
        print("Rating must be a number from 1 to 5.")


def print_reflection(reflection):
    """Display the self-reflection result from the agent."""
    print("\nSelf-Reflection")
    for area in ("relevance", "groundedness", "clarity"):
        item = reflection[area]
        print(f"- {area.title()}: {item['score']}/10 - {item['explanation']}")
    print(f"- Improvement: {reflection['improvement_suggestion']}")


def print_sources(sources):
    """Display policy chunks used by the assistant."""
    if not sources:
        return

    print("\nRetrieved Policy Context")
    for index, source in enumerate(sources, start=1):
        print(
            f"{index}. {source['source']} "
            f"(score: {source['score']:.3f}, chunk: {source['chunk_id']})"
        )


def print_agent_response(response):
    """Display a complete agent response."""
    print("\nAnswer")
    print(response["answer"])

    if response.get("tool_calls"):
        print("\nTool Calls")
        for tool_call in response["tool_calls"]:
            print(f"- {tool_call}")

    print_sources(response.get("sources", []))

    if response.get("reflection"):
        print_reflection(response["reflection"])


def run_cli():
    """Run the menu-driven application."""
    agent = ExpenseAgent()
    last_question = ""
    last_answer = ""

    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            question = prompt_non_empty("Ask your question: ")
            response = agent.answer_question(question)
            print_agent_response(response)
            last_question = question
            last_answer = response["answer"]

        elif choice == "2":
            amount = prompt_amount()
            category = prompt_non_empty("Enter category: ")
            description = prompt_non_empty("Enter description: ")
            response = agent.check_expense_claim(amount, category, description)
            print_agent_response(response)
            last_question = (
                f"Check expense: {amount:.2f} INR, "
                f"{category}, {description}"
            )
            last_answer = response["answer"]

        elif choice == "3":
            policy_name = prompt_non_empty(
                "Enter policy name (travel, meal, reimbursement, approval): "
            )
            response = agent.summarize_policy(policy_name)
            print_agent_response(response)
            last_question = f"Summarize {policy_name} policy"
            last_answer = response["answer"]

        elif choice == "4":
            response = agent.run_evaluation()
            print("\nEvaluation Result")
            print(
                f"Passed: {response['passed']} / {response['total']} "
                f"({response['percentage']:.2f}%)"
            )
            for result in response["results"]:
                status = "PASS" if result["passed"] else "FAIL"
                print(f"- {status}: {result['question']}")
            last_question = "Run evaluation"
            last_answer = (
                f"Passed {response['passed']} out of {response['total']} "
                f"questions."
            )

        elif choice == "5":
            if not last_question or not last_answer:
                print("\nNo previous answer found. Enter feedback manually.")
                last_question = prompt_non_empty("Question: ")
                last_answer = prompt_non_empty("Answer: ")

            rating = prompt_rating()
            result = agent.save_feedback(last_question, last_answer, rating)
            print(result["message"])

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    run_cli()
