from Chapters.CH_15.routing_workflow import classify
from pathlib import Path
import json


# Loading the Dataset
def load_set(path: str) -> list:
    """
    Loads a set of queries from a JSON file.
    """
    with open(path, "r", encoding="utf-8") as f:
        file_contents = json.load(f)

    return file_contents


# Evaluating the Dataset
def evaluate(rows, classify_fn):
    """
    Takes in the List from JSON file and evaluates if LLM is answering correctly
    """
    results = []
    for row in rows:
        """
        Evaluates the LLM's classification against the expected category.
        """
        category = classify_fn(row['query'])
        if row['expected'] == category:
            result = {
                'query': row['query'],
                'expected': row['expected'],
                'predicted': category,
                'tricky': row['tricky'],
                'correct': True
            }
            results.append(result)
        else:
            result = {
                'query': row['query'],
                'expected': row['expected'],
                'predicted': category,
                'tricky': row['tricky'],
                'correct': False
            }
            results.append(result)
        
    return results


def report(results):
    """
    Reports the evaluation results, including overall accuracy and per-category accuracy.
    """
    if results:
        correct_count = sum(1 for result in results if result['correct'])
        tricky_count = sum(1 for result in results if result['tricky'] and result['correct'])
        billing_correct_count = sum(1 for result in results if result['correct'] and result['expected'] == 'billing')
        tech_correct_count = sum(1 for result in results if result['correct'] and result['expected'] == 'tech')
        general_correct_count = sum(1 for result in results if result['correct'] and result['expected'] == 'general')
        accuracy = ((correct_count/len(results))*100)
        total = len(results)
        total_per_category = {
            'billing': sum(1 for result in results if result['expected'] == 'billing'),
            'tech': sum(1 for result in results if result['expected'] == 'tech'),
            'general': sum(1 for result in results if result['expected'] == 'general'),
            'tricky': sum(1 for result in results if result['tricky'])
        }

        print(f"Overall: {correct_count}/{total} = {accuracy:.1f}%")
        print(f"Billing: {billing_correct_count}/{total_per_category['billing']},    Tech: {tech_correct_count}/{total_per_category['tech']},    General: {general_correct_count}/{total_per_category['general']}")
        print(f"Tricky: {tricky_count}/{total_per_category['tricky']}")
        print("Mistakes:")
        
        for i, result in enumerate(results):
            if not result['correct']:
                print(f"Expected: {result['expected']}, Predicted: {result['predicted']} | Query-{i+1}: {result['query'][:55]}...")

        return {'accuracy': f"{accuracy:.1f}%",
                'per_category':{
                                'general': general_correct_count,
                                'tech': tech_correct_count,
                                'billing': billing_correct_count
                                }
                }
    else:
        raise ValueError("No results to report.")


def main():
    """
    Main function to load the dataset, evaluate the queries, and report the results.
    """
    here = Path(__file__).parent
    rows = load_set(here / "routing_set.json")
    results = evaluate(rows, classify)
    summary = report(results)

    with open(here / "results_v1.json", "w") as f:
        json.dump({'summary': summary, 'results': results}, f, indent=4)


if __name__ == "__main__":
    print("I expect 13/15 to pass, and I expect 2 to fail.")
    main()