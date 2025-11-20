# Evaluation Framework

This directory contains evaluation scripts for the AI File Concierge system.

## Running Evaluations

```bash
# Run all evaluation scenarios
python evaluation/test_scenarios.py
```

## Test Scenarios

### 1. Search Accuracy
Tests semantic search quality using predefined queries with known expected results.

**Metrics:**
- Hit@K: Whether expected files appear in top K results
- Average hit rate across all test queries
- Pass rate (percentage of queries with hit rate > 0)

**Test Cases:**
- ML-related code search
- Job application documents
- Meeting notes
- Research paper notes
- Data processing code

### 2. Tagging Quality
Evaluates the relevance of LLM-suggested tags.

**Metrics:**
- Relevance score: Overlap between suggested tags and expected themes
- Success threshold: Relevance > 30%

**Test Files:**
- Resume (expected: career, job, professional themes)
- ML code (expected: machine-learning, python, statistics themes)
- Meeting notes (expected: work, team, planning themes)

### 3. End-to-End Workflow
Tests a complete workflow scenario.

**Steps:**
1. Search for job application files
2. Apply relevant tags to found files
3. Create a collection
4. Add files to the collection

**Metrics:**
- Success rate of individual steps
- Overall workflow completion rate

## Expected Results

A well-functioning system should achieve:
- Search hit rate: >80%
- Tagging relevance: >30%
- Workflow success rate: >90%

## Extending Evaluations

To add new test scenarios:

1. Add test cases to `test_scenarios.py`
2. Define expected results
3. Implement evaluation metrics
4. Update this README with new scenarios
