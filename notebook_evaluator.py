"""
Predictive Analytics Case Study Rubric Evaluator
Scores Jupyter notebooks against 12 criteria (31 total points)
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class NotebookParser:
    """Extract and parse notebook content"""
    
    def __init__(self, notebook_path: str):
        self.notebook_path = Path(notebook_path)
        self.notebook = self._load_notebook()
        self.cells = self.notebook.get('cells', [])
        self.project_root = self.notebook_path.parent
        
    def _load_notebook(self) -> Dict:
        """Load .ipynb file"""
        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Could not load notebook: {e}")
    
    def get_markdown_cells(self) -> List[str]:
        """Extract all markdown cell content"""
        return [
            cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])
            for cell in self.cells if cell['cell_type'] == 'markdown'
        ]
    
    def get_code_cells(self) -> List[str]:
        """Extract all code cell content"""
        return [
            cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])
            for cell in self.cells if cell['cell_type'] == 'code'
        ]
    
    def get_outputs(self) -> List[Dict]:
        """Extract cell outputs"""
        outputs = []
        for cell in self.cells:
            if cell.get('outputs'):
                outputs.extend(cell['outputs'])
        return outputs
    
    def get_file_in_project(self, filename: str) -> bool:
        """Check if file exists in project directory"""
        return (self.project_root / filename).exists()


class CriterionEvaluator:
    """Evaluate each rubric criterion"""
    
    def __init__(self, parser: NotebookParser):
        self.parser = parser
        self.markdown = '\n'.join(parser.get_markdown_cells())
        self.code = '\n'.join(parser.get_code_cells())
        self.outputs = parser.get_outputs()
    
    # Criterion 1: Problem Definition & Business Context (0-3)
    def evaluate_problem_definition(self) -> Tuple[int, str]:
        """Assess problem definition and business context"""
        score = 0
        observations = []
        
        business_keywords = [
            'business', 'objective', 'goal', 'stakeholder', 'impact', 'problem statement',
            'context', 'success criteria', 'justification', 'motivation'
        ]
        
        text_lower = self.markdown.lower()
        keyword_matches = sum(1 for kw in business_keywords if kw in text_lower)
        
        # Check if problem is defined at all
        if not self.markdown or len(self.markdown.strip()) < 100:
            score = 0
            observations.append("No meaningful problem definition found")
        elif keyword_matches >= 5:
            score = 3
            observations.append("Comprehensive problem definition with business context and objectives")
        elif keyword_matches >= 3:
            score = 2
            observations.append("Clear problem description with business relevance")
        elif keyword_matches >= 1:
            score = 1
            observations.append("Problem mentioned but lacks full business context")
        else:
            score = 0
            observations.append("Problem definition is unclear or missing business context")
        
        return score, "; ".join(observations)
    
    # Criterion 2: Data Acquisition & Understanding (0-3)
    def evaluate_data_acquisition(self) -> Tuple[int, str]:
        """Assess data source, quality, and suitability"""
        score = 0
        observations = []
        
        data_keywords = ['data source', 'dataset', 'csv', 'api', 'download', 'collection',
                        'provenance', 'quality', 'limitation', 'assumption', 'suitability']
        
        text_lower = self.markdown.lower()
        keyword_matches = sum(1 for kw in data_keywords if kw in text_lower)
        
        # Check for actual data loading code
        has_data_loading = bool(re.search(r'(pd\.read|load|download|fetch)', self.code, re.I))
        
        if not self.markdown or not has_data_loading:
            score = 0
            observations.append("No data acquisition description or code found")
        elif keyword_matches >= 5 and has_data_loading:
            score = 3
            observations.append("Comprehensive data discussion including provenance, quality, and limitations")
        elif keyword_matches >= 3 and has_data_loading:
            score = 2
            observations.append("Data source and collection method explained")
        elif has_data_loading:
            score = 1
            observations.append("Dataset identified with minimal explanation")
        else:
            score = 0
            observations.append("Insufficient data source documentation")
        
        return score, "; ".join(observations)
    
    # Criterion 3: Data Preparation & EDA (0-3)
    def evaluate_data_prep_eda(self) -> Tuple[int, str]:
        """Assess preprocessing and exploratory data analysis"""
        score = 0
        observations = []
        
        eda_patterns = [
            r'(describe|info|shape|head|tail)',  # Basic stats
            r'(dropna|fillna|drop|isnull|missing)',  # Missing value handling
            r'(corr|correlation|heatmap)',  # Correlations
            r'(plot|hist|scatter|boxplot|kde|distribution)',  # Visualizations
            r'(outlier|zscore|iqr|percentile)',  # Outlier detection
            r'(scale|normalize|standardize|preprocessing)',  # Preprocessing
            r'(feature.*engineering|create.*feature|derive)',  # Feature engineering
        ]
        
        pattern_matches = sum(1 for pattern in eda_patterns if re.search(pattern, self.code, re.I))
        viz_count = sum(1 for pattern in eda_patterns[2:5] if re.search(pattern, self.code, re.I))
        
        if pattern_matches == 0:
            score = 0
            observations.append("No preprocessing or exploratory analysis found")
        elif pattern_matches >= 5 and viz_count >= 2:
            score = 3
            observations.append("Extensive EDA with feature engineering, outlier treatment, and quality assessment")
        elif pattern_matches >= 3 and viz_count >= 1:
            score = 2
            observations.append("Missing value handling, feature analysis, distributions, and visualizations present")
        elif pattern_matches >= 1:
            score = 1
            observations.append("Basic cleaning and summary statistics")
        else:
            score = 0
            observations.append("Insufficient data preparation and exploration")
        
        return score, "; ".join(observations)
    
    # Criterion 4: Visualizations & Analytical Communication (0-3)
    def evaluate_visualizations(self) -> Tuple[int, str]:
        """Assess visualization quality and analytical communication"""
        score = 0
        observations = []
        
        # Check for visualization libraries
        viz_imports = sum(1 for lib in ['matplotlib', 'seaborn', 'plotly'] 
                         if re.search(f'import.*{lib}|from.*{lib}', self.code, re.I))
        
        # Check for visualization code
        plot_patterns = [
            r'(plt\.plot|plt\.hist|plt\.scatter|plt\.bar)',
            r'(sns\.plot|sns\.heatmap|sns\.boxplot)',
            r'(px\.|plotly\.express)',
            r'(\.plot\(|\.scatter\(|\.bar\()',
        ]
        plot_count = sum(1 for pattern in plot_patterns if re.search(pattern, self.code, re.I))
        
        # Check for labels and titles
        has_labels = bool(re.search(r'(xlabel|ylabel|title|set_title|label=)', self.code, re.I))
        
        if plot_count == 0:
            score = 0
            observations.append("No visualizations found or visualizations provide little analytical value")
        elif plot_count >= 8 and has_labels and viz_imports > 0:
            score = 3
            observations.append("Advanced visualizations including feature importance, ROC curves, or residual analysis")
        elif plot_count >= 5 and has_labels and viz_imports > 0:
            score = 2
            observations.append("Multiple chart types with clear labels and trend/distribution analysis")
        elif plot_count >= 2 and has_labels:
            score = 1
            observations.append("Basic visualizations present with titles and labels")
        else:
            score = 0
            observations.append("Insufficient or irrelevant visualizations")
        
        return score, "; ".join(observations)
    
    # Criterion 5: Modeling Approach & Theory (0-4)
    def evaluate_modeling_approach(self) -> Tuple[int, str]:
        """Assess model selection and theoretical justification"""
        score = 0
        observations = []
        
        # Check for model implementations
        model_imports = [
            r'(RandomForest|LogisticRegression|SVM|XGBoost|Gradient)',
            r'(LinearRegression|Ridge|Lasso)',
            r'(KMeans|DBSCAN|Hierarchical)',
            r'(from.*ensemble|from.*tree|from.*linear_model)',
        ]
        model_count = sum(1 for pattern in model_imports if re.search(pattern, self.code, re.I))
        
        # Check for validation and tuning
        has_cv = bool(re.search(r'(cross_val|GridSearchCV|RandomizedSearchCV|KFold)', self.code, re.I))
        has_tuning = bool(re.search(r'(param_grid|hyperparameter|tuning)', self.code, re.I))
        
        # Check for theoretical discussion
        theory_keywords = ['assumption', 'trade-off', 'rationale', 'why', 'because', 'model selection']
        theory_matches = sum(1 for kw in theory_keywords if kw in self.markdown.lower())
        
        if model_count == 0:
            score = 0
            observations.append("No model development")
        elif model_count >= 3 and has_cv and has_tuning and theory_matches >= 2:
            score = 4
            observations.append("Deep understanding of predictive analytics with multiple models and rigorous evaluation")
        elif model_count >= 2 and has_cv and theory_matches >= 1:
            score = 3
            observations.append("Multiple models compared with detailed justification")
        elif model_count >= 2:
            score = 2
            observations.append("Multiple models evaluated with basic rationale")
        elif model_count >= 1:
            score = 1
            observations.append("Single model with minimal explanation")
        
        return score, "; ".join(observations)
    
    # Criterion 6: Evaluation & Results (0-4)
    def evaluate_evaluation_results(self) -> Tuple[int, str]:
        """Assess metrics and result interpretation"""
        score = 0
        observations = []
        
        # Check for evaluation metrics
        metric_patterns = [
            r'(accuracy|precision|recall|f1_score|roc_auc)',
            r'(confusion_matrix|classification_report)',
            r'(mse|rmse|mae|r2_score)',
            r'(cross_val_score)',
        ]
        metric_count = sum(1 for pattern in metric_patterns if re.search(pattern, self.code, re.I))
        
        # Check for error analysis
        has_error_analysis = bool(re.search(r'(error|residual|prediction.*error|feature_importance)', 
                                            self.code, re.I))
        
        # Check for business interpretation
        has_business_interpretation = bool(re.search(r'(business|objective|decision|impact|recommendation)',
                                                     self.markdown, re.I))
        
        if metric_count == 0:
            score = 0
            observations.append("No evaluation performed")
        elif metric_count >= 3 and has_error_analysis and has_business_interpretation:
            score = 4
            observations.append("Comprehensive evaluation with error analysis and business interpretation")
        elif metric_count >= 3 and has_business_interpretation:
            score = 3
            observations.append("Metrics explained and connected to business objectives")
        elif metric_count >= 2:
            score = 2
            observations.append("Appropriate metrics reported")
        elif metric_count >= 1:
            score = 1
            observations.append("Results reported without detailed metrics justification")
        
        return score, "; ".join(observations)
    
    # Criterion 7: Deployment & Operationalization (0-3)
    def evaluate_deployment(self) -> Tuple[int, str]:
        """Assess deployment architecture and strategy"""
        score = 0
        observations = []
        
        deployment_keywords = ['deploy', 'production', 'monitoring', 'maintenance', 'scaling',
                              'api', 'inference', 'pipeline', 'retraining', 'governance']
        
        text_lower = self.markdown.lower()
        keyword_matches = sum(1 for kw in deployment_keywords if kw in text_lower)
        
        if keyword_matches == 0:
            score = 0
            observations.append("No deployment discussion")
        elif keyword_matches >= 5:
            score = 3
            observations.append("End-to-end operationalization including scalability, monitoring, and retraining")
        elif keyword_matches >= 3:
            score = 2
            observations.append("Deployment architecture and maintenance considerations discussed")
        elif keyword_matches >= 1:
            score = 1
            observations.append("Basic deployment concept described")
        
        return score, "; ".join(observations)
    
    # Criterion 8: Business Impact & Recommendations (0-3)
    def evaluate_business_impact(self) -> Tuple[int, str]:
        """Assess business impact and actionable recommendations"""
        score = 0
        observations = []
        
        impact_keywords = ['recommendation', 'action', 'roi', 'outcome', 'impact', 'decision',
                          'roadmap', 'future', 'business value', 'stakeholder']
        
        text_lower = self.markdown.lower()
        keyword_matches = sum(1 for kw in impact_keywords if kw in text_lower)
        
        if keyword_matches == 0:
            score = 0
            observations.append("No discussion of impact")
        elif keyword_matches >= 5:
            score = 3
            observations.append("Clear business outcomes, ROI, decision support value, and future roadmap")
        elif keyword_matches >= 3:
            score = 2
            observations.append("Actionable recommendations derived from findings")
        elif keyword_matches >= 1:
            score = 1
            observations.append("General conclusions provided")
        
        return score, "; ".join(observations)
    
    # Criterion 9: Reflection & Future Improvements (0-2)
    def evaluate_reflection(self) -> Tuple[int, str]:
        """Assess limitations and future improvements discussion"""
        score = 0
        observations = []
        
        reflection_keywords = ['limitation', 'lesson', 'challenge', 'future', 'improvement',
                              'alternative', 'drift', 'retrain', 'enhance']
        
        text_lower = self.markdown.lower()
        keyword_matches = sum(1 for kw in reflection_keywords if kw in text_lower)
        
        if keyword_matches == 0:
            score = 0
            observations.append("No reflection")
        elif keyword_matches >= 4:
            score = 2
            observations.append("Thorough discussion of limitations, retraining needs, and enhancements")
        elif keyword_matches >= 1:
            score = 1
            observations.append("Some limitations or lessons learned discussed")
        
        return score, "; ".join(observations)
    
    # Criterion 10: Code Export & Reproducibility (0-2)
    def evaluate_reproducibility(self) -> Tuple[int, str]:
        """Assess script export and reproducibility"""
        score = 0
        observations = []
        
        # Check for standalone script export
        has_script_export = any(self.parser.get_file_in_project(f) 
                               for f in ['train.py', 'main.py', 'run.py', 'model.py'])
        
        # Check for requirements documentation
        has_requirements = any(self.parser.get_file_in_project(f) 
                              for f in ['requirements.txt', 'Pipfile', 'environment.yml', 'pyproject.toml'])
        
        # Check for dataset access info
        has_data_info = bool(re.search(r'(download|url|path|data\s*\.|dataset)', self.markdown, re.I))
        
        if has_script_export and has_requirements and has_data_info:
            score = 2
            observations.append("Notebook and training script execute end-to-end with documented dependencies")
        elif has_script_export and has_requirements:
            score = 1
            observations.append("Training logic exported and dependencies documented")
        elif has_script_export or has_requirements:
            score = 1
            observations.append("Partial reproducibility setup present")
        else:
            score = 0
            observations.append("No script export or missing dataset/dependencies")
        
        return score, "; ".join(observations)
    
    # Criterion 11: Containerization & Environment (0-2)
    def evaluate_containerization(self) -> Tuple[int, str]:
        """Assess containerization and environment setup"""
        score = 0
        observations = []
        
        # Check for containerization files
        has_dockerfile = any(self.parser.get_file_in_project(f) 
                            for f in ['Dockerfile', 'docker-compose.yml', '.dockerignore'])
        
        # Check for dependency management
        has_dependencies = any(self.parser.get_file_in_project(f) 
                              for f in ['requirements.txt', 'Pipfile', 'environment.yml', 'pyproject.toml'])
        
        # Check for README with instructions
        has_readme = self.parser.get_file_in_project('README.md') or self.parser.get_file_in_project('README.rst')
        
        if has_dockerfile and has_dependencies and has_readme:
            score = 2
            observations.append("Fully containerized with build and run instructions in README")
        elif has_dockerfile and has_dependencies:
            score = 1
            observations.append("Dockerfile and dependencies provided")
        elif has_dependencies and has_readme:
            score = 1
            observations.append("Dependencies and setup documentation present")
        else:
            score = 0
            observations.append("No containerization or dependency management")
        
        return score, "; ".join(observations)
    
    # Criterion 12: Cloud Deployment & Live Testing (0-2)
    def evaluate_cloud_deployment(self) -> Tuple[int, str]:
        """Assess cloud deployment and live testing"""
        score = 0
        observations = []
        
        # Check for cloud configuration files
        has_cloud_config = any(self.parser.get_file_in_project(f) 
                              for f in ['app.yaml', 'cloudbuild.yaml', 'terraform.tf', 'k8s.yaml', 
                                       '.github/workflows', 'deployment.yaml', 'helm-chart'])
        
        # Check for cloud deployment discussion or URLs
        deployment_indicators = bool(re.search(
            r'(aws|gcp|azure|cloud run|ec2|heroku|kubernetes|k8s|deployed|production.*url|live)',
            self.markdown, re.I
        ))
        
        if has_cloud_config and deployment_indicators:
            score = 2
            observations.append("Cloud deployment with configuration files and evidence of live deployment")
        elif has_cloud_config or deployment_indicators:
            score = 1
            observations.append("Cloud deployment documentation or configuration present")
        else:
            score = 0
            observations.append("No cloud deployment or live testing evidence")
        
        return score, "; ".join(observations)


class ScoringEngine:
    """Aggregate and calculate final scores"""
    
    def __init__(self, evaluator: CriterionEvaluator):
        self.evaluator = evaluator
    
    def evaluate_all(self) -> Dict[str, Any]:
        """Run all evaluations and compile results"""
        
        criteria = [
            ("Problem Definition & Business Context", self.evaluator.evaluate_problem_definition, 3),
            ("Data Acquisition & Understanding", self.evaluator.evaluate_data_acquisition, 3),
            ("Data Preparation & EDA", self.evaluator.evaluate_data_prep_eda, 3),
            ("Visualizations & Analytical Communication", self.evaluator.evaluate_visualizations, 3),
            ("Modeling Approach & Theory", self.evaluator.evaluate_modeling_approach, 4),
            ("Evaluation & Results", self.evaluator.evaluate_evaluation_results, 4),
            ("Deployment & Operationalization", self.evaluator.evaluate_deployment, 3),
            ("Business Impact & Recommendations", self.evaluator.evaluate_business_impact, 3),
            ("Reflection & Future Improvements", self.evaluator.evaluate_reflection, 2),
            ("Code Export & Reproducibility", self.evaluator.evaluate_reproducibility, 2),
            ("Containerization & Environment", self.evaluator.evaluate_containerization, 2),
            ("Cloud Deployment & Live Testing", self.evaluator.evaluate_cloud_deployment, 2),
        ]
        
        results = []
        total_score = 0
        max_score = 0
        
        for name, evaluator_func, max_points in criteria:
            score, observations = evaluator_func()
            # Clamp score to max_points
            score = min(score, max_points)
            results.append({
                "criterion": name,
                "score": score,
                "max_points": max_points,
                "observations": observations,
            })
            total_score += score
            max_score += max_points
        
        return {
            "criteria": results,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round((total_score / max_score * 100), 2) if max_score > 0 else 0,
        }


class ReportGenerator:
    """Generate formatted evaluation reports"""
    
    @staticmethod
    def generate_report(scores: Dict[str, Any], verbose: bool = True) -> str:
        """Generate formatted report"""
        
        lines = [
            "=" * 80,
            "PREDICTIVE ANALYTICS CASE STUDY RUBRIC EVALUATION",
            "=" * 80,
            "",
        ]
        
        for criterion in scores["criteria"]:
            lines.append(f"[{criterion['score']}/{criterion['max_points']}] {criterion['criterion']}")
            lines.append(f"     {criterion['observations']}")
            lines.append("")
        
        lines.extend([
            "=" * 80,
            f"TOTAL SCORE: {scores['total_score']}/{scores['max_score']} ({scores['percentage']}%)",
            "=" * 80,
            "",
        ])
        
        # Add performance tier
        percentage = scores["percentage"]
        if percentage >= 90:
            tier = "EXCELLENT - Project demonstrates comprehensive analytics maturity"
        elif percentage >= 80:
            tier = "VERY GOOD - Project shows strong analytics practices with minor gaps"
        elif percentage >= 70:
            tier = "GOOD - Project covers core analytics requirements"
        elif percentage >= 60:
            tier = "FAIR - Project needs improvement in several areas"
        else:
            tier = "NEEDS WORK - Significant gaps in analytics practices"
        
        lines.append(f"Performance Tier: {tier}")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_json(scores: Dict[str, Any]) -> str:
        """Generate JSON report"""
        return json.dumps(scores, indent=2)


class NotebookEvaluator:
    """Main evaluator interface"""
    
    def __init__(self, notebook_path: str):
        """Initialize evaluator with notebook path"""
        self.parser = NotebookParser(notebook_path)
        self.evaluator = CriterionEvaluator(self.parser)
        self.scorer = ScoringEngine(self.evaluator)
    
    def evaluate(self, format: str = "text") -> str:
        """Evaluate notebook and return report
        
        Args:
            format: "text" for formatted report, "json" for JSON
        
        Returns:
            Formatted evaluation report
        """
        scores = self.scorer.evaluate_all()
        
        if format == "json":
            return ReportGenerator.generate_json(scores)
        else:
            return ReportGenerator.generate_report(scores)
    
    def evaluate_structured(self) -> Dict[str, Any]:
        """Evaluate notebook and return structured results"""
        return self.scorer.evaluate_all()


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python notebook_evaluator.py <notebook_path> [--json]")
        sys.exit(1)
    
    notebook_path = sys.argv[1]
    output_format = "json" if "--json" in sys.argv else "text"
    
    try:
        evaluator = NotebookEvaluator(notebook_path)
        report = evaluator.evaluate(format=output_format)
        print(report)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
