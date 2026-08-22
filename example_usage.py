#!/usr/bin/env python
"""
Example: Using the NotebookEvaluator in Python code

This demonstrates programmatic use of the evaluator for batch processing,
custom reporting, or integration into other tools.
"""

from notebook_evaluator import NotebookEvaluator
import json
from pathlib import Path


def evaluate_single_notebook(notebook_path: str):
    """Evaluate a single notebook and print results"""
    print(f"\nEvaluating: {notebook_path}")
    print("=" * 80)
    
    try:
        evaluator = NotebookEvaluator(notebook_path)
        results = evaluator.evaluate_structured()
        
        # Print summary
        print(f"Score: {results['total_score']}/{results['max_score']} ({results['percentage']}%)\n")
        
        # Print each criterion
        for criterion in results['criteria']:
            status = "✓" if criterion['score'] == criterion['max_points'] else "✗"
            print(f"{status} [{criterion['score']}/{criterion['max_points']}] {criterion['criterion']}")
            print(f"  → {criterion['observations']}\n")
        
        return results
    
    except Exception as e:
        print(f"Error evaluating {notebook_path}: {e}")
        return None


def evaluate_directory(directory: str) -> list:
    """Evaluate all notebooks in a directory"""
    print(f"\nEvaluating all notebooks in: {directory}")
    print("=" * 80)
    
    notebook_dir = Path(directory)
    notebooks = list(notebook_dir.rglob("*.ipynb"))
    results = []
    
    for notebook_path in notebooks:
        result = evaluate_single_notebook(str(notebook_path))
        if result:
            result['notebook_path'] = str(notebook_path)
            results.append(result)
    
    return results


def generate_summary_report(results: list):
    """Generate a summary report for multiple notebooks"""
    if not results:
        print("No results to report")
        return
    
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    total_notebooks = len(results)
    average_score = sum(r['total_score'] for r in results) / total_notebooks
    
    print(f"\nTotal Notebooks Evaluated: {total_notebooks}")
    print(f"Average Score: {average_score:.2f}/{results[0]['max_score']} ({average_score/results[0]['max_score']*100:.1f}%)\n")
    
    # Sort by score
    sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    print("Notebooks Ranked by Score:")
    print("-" * 80)
    for i, result in enumerate(sorted_results, 1):
        notebook_name = Path(result['notebook_path']).name
        score = result['total_score']
        percentage = result['percentage']
        print(f"{i}. {notebook_name}")
        print(f"   Score: {score}/{result['max_score']} ({percentage}%)\n")
    
    # Criteria performance
    print("\nCriteria Performance Across All Notebooks:")
    print("-" * 80)
    
    criteria_scores = {}
    for result in results:
        for criterion in result['criteria']:
            name = criterion['criterion']
            if name not in criteria_scores:
                criteria_scores[name] = []
            criteria_scores[name].append(criterion['score'] / criterion['max_points'] * 100)
    
    for name, scores in sorted(criteria_scores.items()):
        avg_score = sum(scores) / len(scores)
        print(f"{name}: {avg_score:.1f}%")


if __name__ == "__main__":
    notebook_path = r"C:\Users\gyanr\gyan-python-workspace\ml-capstones\heart-prediction-explainability\dsc-680-heart_disease_prediction.ipynb"
    evaluate_single_notebook(notebook_path)
    import sys
    
    # if len(sys.argv) < 2:
    #     print("Usage:")
    #     print("  python example_usage.py <notebook_path>              # Evaluate single notebook")
    #     print("  python example_usage.py --dir <directory>            # Evaluate all notebooks in directory")
    #     print("  python example_usage.py --report <json_file>         # Generate report from saved results")
    #     sys.exit(1)
    
    # if sys.argv[1] == "--dir" and len(sys.argv) > 2:
    #     # Batch evaluate directory
    #     results = evaluate_directory(sys.argv[2])
    #     generate_summary_report(results)
    #
    #     # Optionally save results
    #     if len(sys.argv) > 3 and sys.argv[3] == "--save":
    #         output_file = "evaluation_results.json"
    #         with open(output_file, 'w') as f:
    #             json.dump(results, f, indent=2)
    #         print(f"\nResults saved to {output_file}")
    #
    # else:
    #     # Single notebook evaluation
    #     # notebook_path = sys.argv[1]
    #     notebook_path = r"C:\Users\gyanr\gyan-python-workspace\ml-capstones\heart-prediction-explainability\dsc-680-heart_disease_prediction.ipynb"
    #     evaluate_single_notebook(notebook_path)
