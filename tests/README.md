# NutriGrove Backend Test Suite

Comprehensive test suite for the NutriGrove Backend API, covering API endpoints, Pydantic models, and the AI food recommendation system.

## Test Coverage

### 1. Pydantic Model Tests (`test_schema.py`)
- **Valid Data Validation**: Ensures valid user input passes all validation rules
- **BMI Calculation**: Verifies computed field calculations
- **Field Validation**: Tests constraints on age, weight, height, calories, and protein
- **Edge Cases**: Tests boundary values and empty inputs
- **Error Handling**: Validates that invalid data raises ValidationError

### 2. API Endpoint Tests (`test_api.py`)
- **GET /**: Root endpoint functionality
- **POST /recommendations**:
  - Success cases with valid data (200 status)
  - Invalid data validation (422 status)
  - Response structure verification
  - Edge case handling
- **GET /menu**: Menu data retrieval
- **Error Handling**: Tests for wrong HTTP methods and invalid requests

### 3. FoodRecommender Tests (`test_food_recommender.py`)
- **Initialization**: Environment variable validation and client setup
- **Menu Data Retrieval**: Database queries and caching
- **Data Formatting**: Menu data transformation and disclaimer removal
- **Meal Schedule Generation**: AI integration and response parsing
- **Error Handling**: Database failures, AI errors, and JSON parsing

## Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_schema.py
pytest tests/test_api.py
pytest tests/test_food_recommender.py
```

### Run Tests with Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test Class or Function
```bash
pytest tests/test_schema.py::TestUserInputModel::test_valid_user_input
pytest tests/test_api.py::TestRecommendationsEndpoint
```

## Test Structure

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_schema.py                 # Pydantic model tests
├── test_api.py                    # API endpoint tests
└── test_food_recommender.py       # FoodRecommender class tests
```

## Key Testing Patterns

### Mocking External Services
Tests use mocking to isolate components:
- **Supabase Database**: Mocked to avoid real database calls
- **Google Gemini API**: Mocked to avoid API costs and ensure deterministic tests
- **Environment Variables**: Controlled via `monkeypatch` fixture

### Fixtures
Common fixtures are defined in `conftest.py` for reuse across test files.

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Common Test Scenarios

### Testing Valid API Request
```python
def test_recommendations_success(client, valid_user_data, mock_meal_schedule):
    response = client.post("/recommendations", json=valid_user_data)
    assert response.status_code == 200
```

### Testing Invalid Data
```python
def test_recommendations_invalid_age(client, valid_user_data):
    invalid_data = valid_user_data.copy()
    invalid_data["age"] = -5
    response = client.post("/recommendations", json=invalid_data)
    assert response.status_code == 422
```

### Testing Pydantic Validation
```python
def test_age_validation_negative():
    with pytest.raises(ValidationError) as exc_info:
        UserInput(age=-5, ...)
    assert "age" in str(exc_info.value)
```

## CI/CD Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest --cov=backend
```

## Test Metrics

The test suite covers:
- ✅ 20+ Pydantic model validation scenarios
- ✅ 25+ API endpoint test cases
- ✅ 15+ FoodRecommender integration tests
- ✅ Error handling and edge cases
- ✅ Response format validation
- ✅ Data type validation

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on others
2. **Mocking**: External services are mocked to ensure fast, reliable tests
3. **Clarity**: Test names clearly describe what is being tested
4. **Coverage**: Both happy paths and error scenarios are tested
5. **Maintainability**: Fixtures reduce code duplication

## Troubleshooting

### Import Errors
Ensure you're running pytest from the project root:
```bash
cd "C:\My Projects\NutriGrove\NutriGrove Backend"
pytest
```

### Environment Variable Issues
Tests mock environment variables, but ensure no conflicting `.env` files interfere.

### Async Test Issues
If you encounter async-related errors, ensure `pytest-asyncio` is installed.

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass before committing
3. Maintain test coverage above 80%
4. Follow existing naming conventions
