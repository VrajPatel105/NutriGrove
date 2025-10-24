# Testing Quick Start Guide

## Installation
```bash
pip install -r requirements.txt
```

## Run All Tests
```bash
pytest
```

## Common Commands

### Run with coverage
```bash
pytest --cov=backend.app --cov-report=term-missing
```

### Run verbose
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_api.py
pytest tests/test_schema.py
pytest tests/test_food_recommender.py
```

### Run specific test
```bash
pytest tests/test_api.py::TestRecommendationsEndpoint::test_recommendations_success
```

## Test Results
- **Total Tests:** 65
- **Status:** ✅ All Passing
- **Coverage:** 97%
- **Execution Time:** ~6 seconds

## What's Tested

### API Endpoints (/recommendations, /menu, /)
- ✅ Success responses (200)
- ✅ Validation errors (422)
- ✅ Invalid HTTP methods (405)
- ✅ Response structure
- ✅ Edge cases

### Pydantic Models
- ✅ Valid data acceptance
- ✅ Invalid data rejection
- ✅ Field constraints (age, weight, height, etc.)
- ✅ Type validation
- ✅ Edge cases

### FoodRecommender Service
- ✅ Initialization & configuration
- ✅ Database operations
- ✅ AI integration
- ✅ Error handling
- ✅ Data formatting

## File Structure
```
tests/
├── test_api.py              # 28 API tests
├── test_schema.py           # 20 model tests
├── test_food_recommender.py # 17 service tests
├── conftest.py              # Shared fixtures
└── README.md                # Full documentation
```

## For Okta Interview
Key points to mention:
1. 97% code coverage
2. 65 comprehensive tests
3. Production-level code quality
4. Proper mocking of external services
5. Fast execution (<10 seconds)
6. CI/CD ready
