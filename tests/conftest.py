import pytest
import shutil
import os


@pytest.fixture
def job_dir(tmp_path):
    """
    Fixture to provide a job directory path within a temporary path.
    Does NOT create the directory, allowing create_job_dir to handle it.
    """
    jd = tmp_path / "job"
    # Do NOT create the directory here
    return jd


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to execute after each test to check for failures and copy the job directory if the test fails.
    """
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # Only act on actual test function calls, not setup/teardown
    if rep.when == "call" and rep.failed:
        # Access the 'job_dir' from the test function's arguments
        job_dir = item.funcargs.get('job_dir')
        if job_dir and job_dir.exists():
            # Define a path to copy the failed job_dir for inspection
            failed_tests_root = os.path.join(os.path.dirname(__file__), 'failed_tests')
            os.makedirs(failed_tests_root, exist_ok=True)
            failed_dir = os.path.join(failed_tests_root, item.name)

            # Remove the failed_dir if it already exists to avoid shutil.copytree error
            if os.path.exists(failed_dir):
                shutil.rmtree(failed_dir)

            shutil.copytree(job_dir, failed_dir)
            print(f"\nTest failed. Job directory copied to: {failed_dir}")
