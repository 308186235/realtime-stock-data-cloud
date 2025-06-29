@echo off
setlocal

echo Running integration tests for enhanced trading features...

REM Check if venv exists and activate it
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please ensure setup is complete.
    exit /b 1
)

REM Create a directory for test results if it doesn't exist
if not exist backend\tests\test_results mkdir backend\tests\test_results

REM Display help menu if requested
if "%1"=="help" (
    echo Available commands:
    echo   run_integration_tests.bat          - Run all integration tests
    echo   run_integration_tests.bat component - Run individual component tests
    echo   run_integration_tests.bat perf      - Run performance tests
    echo   run_integration_tests.bat perf indicators - Run only indicator performance tests
    echo   run_integration_tests.bat perf backtest  - Run only backtest performance tests
    echo   run_integration_tests.bat perf memory    - Run only memory usage tests
    echo   run_integration_tests.bat help      - Display this help message
    exit /b 0
)

REM Check if performance tests are requested
if "%1"=="perf" (
    echo Running performance tests...
    
    if "%2"=="" (
        python backend\tests\performance_test.py
    ) else (
        python backend\tests\performance_test.py %2
    )
    
    if %ERRORLEVEL% neq 0 (
        echo Performance tests failed with error code %ERRORLEVEL%
        exit /b %ERRORLEVEL%
    )
    
    echo Performance tests completed successfully!
    exit /b 0
)

REM Run the appropriate integration tests
if "%1"=="component" (
    echo Running component integration tests...
    python backend\tests\run_integration_tests.py component
) else (
    echo Running full integration test suite...
    python backend\tests\run_integration_tests.py
)

REM Check the exit code
if %ERRORLEVEL% neq 0 (
    echo Integration tests failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Integration tests completed successfully!
endlocal 