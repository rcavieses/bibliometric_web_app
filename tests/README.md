# Testing Guide for Bibliometric Web App

This guide explains how to run tests for the Bibliometric Web App, including Docker-based testing and Firebase integration tests.

## Prerequisites

Before running tests, ensure you have:

1. Docker and Docker Compose installed
2. Firebase credentials set up (for Firebase integration tests)
3. All required API keys in the `secrets` directory

## Test Structure

The test suite is organized as follows:

- `unit/`: Unit tests for individual components
  - `test_firebase_integration.py`: Tests for Firebase integration
  - `test_streamlit_ui.py`: Tests for Streamlit UI components
- `integration/`: Integration tests for multiple components
- `conftest.py`: Pytest fixtures and configuration
- `Dockerfile.test`: Docker configuration for testing
- `docker-compose.test.yml`: Docker Compose configuration for testing

## Running Tests with Docker

The recommended way to run tests is using Docker, which ensures a consistent environment:

```bash
# Navigate to the tests directory
cd tests

# Run all tests
docker-compose -f docker-compose.test.yml up

# Run tests with cleanup
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test
docker-compose -f docker-compose.test.yml down
```

This will:
1. Build a test Docker image
2. Mount the necessary volumes
3. Run the pytest suite
4. Display the test results

## Running Tests Locally

You can also run tests directly on your local machine:

```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_firebase_integration.py

# Run tests with coverage
python -m pytest --cov=src
```

## Testing Firebase Integration

Firebase integration tests verify that:

1. Authentication works properly
2. Firestore database operations succeed
3. API key management functions correctly
4. User management works as expected

To run these tests, you must have:
- A valid `firebase_credentials.json` file in the `secrets` directory
- Firebase project configured as described in `docs/guides/firebase_setup.md`

The tests use mocking to avoid making actual API calls to Firebase in most cases.

## Testing Web Application

The web application tests verify that:

1. UI components render correctly
2. User interactions work as expected
3. Pipeline execution succeeds
4. Results are properly displayed

To run the web application in test mode:

```bash
# Using Docker
docker-compose -f docker-compose.test.yml up web-test

# Or locally
TESTING=1 streamlit run src/web/streamlit_app.py
```

## Continuous Integration

For CI/CD pipelines, you can use the following command:

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test
```

This will exit with a non-zero code if any tests fail, making it suitable for CI environments.

## Troubleshooting

### Common Issues

- **Missing Secret Files**: Ensure all required secret files are present in the `secrets` directory
- **Docker Connection Issues**: Verify Docker is running and you have sufficient permissions
- **Firebase Authentication Failures**: Check your Firebase credentials and project setup
- **Test Timeouts**: Some tests might timeout when making external API calls; consider increasing timeouts for integration tests

### Getting Test Logs

To see detailed test logs:

```bash
# Run with verbose output
docker-compose -f docker-compose.test.yml run test pytest -v

# Get container logs
docker-compose -f docker-compose.test.yml logs
```

## Adding New Tests

When adding new tests:

1. For unit tests, add to the appropriate file in `tests/unit/`
2. For integration tests, add to `tests/integration/`
3. Add fixtures to `conftest.py` as needed
4. Run the tests to ensure they pass