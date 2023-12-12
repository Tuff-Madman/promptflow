import argparse
import os
import sys
from pathlib import Path

from utils import Color, run_command, print_red

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"{Color.RED}Test Coverage for Promptflow!{Color.END}"
        + "\n"
    )

    parser.add_argument("-p", required=True, nargs="+", help="The paths to calculate code coverage")
    parser.add_argument("-t", required=True, nargs="+", help="The path to the tests")
    parser.add_argument("-l", required=True, help="Location to run tests in")
    parser.add_argument(
        "-m",
        required=True,
        help="Pytest marker to identify the tests to run",
        default="all",
    )
    parser.add_argument(
        "-o",
        required=False,
        help="Pytest output file name",
        default="test-results.xml",
    )
    parser.add_argument("-n", help="Pytest number of process to run the tests", default="auto")
    parser.add_argument(
        "--model-name",
        help="The model file name to run the tests",
        type=str,
        default="",
    )
    parser.add_argument("--timeout", help="Timeout for individual tests (seconds)", type=str, default="")
    parser.add_argument(
        "--coverage-config",
        help="The path of code coverage config file",
        type=str,
        default="",
    )
    parser.add_argument(
        "--disable-cov-branch",
        action="store_true",
        help="Whether to enable branch coverage calculation",
    )
    parser.add_argument(
        "--ignore-glob",
        help="The path of ignored test file",
        type=str,
        default="",
    )

    args = parser.parse_args()
    print(f"Working directory: {os.getcwd()}")
    print(f"Args.p: {str(args.p)}")
    print(f"Args.t: {str(args.t)}")
    print(f"Args.l: {str(args.l)}")
    print(f"Args.m: {str(args.m)}")
    print(f"Args.n: {str(args.n)}")
    print(f"Args.o: {str(args.o)}")
    print(f"Args.model-name: {str(args.model_name)}")
    print(f"Args.timeout: {str(args.timeout)}")
    print(f"Args.coverage-config: {str(args.coverage_config)}")
    print(f"Args.ignore-glob: {str(args.ignore_glob)}")
    print(f"Args.disable-cov-branch: {str(args.disable_cov_branch)}")

    test_paths_list = [str(Path(path).absolute()) for path in args.t]

    # display a list of all Python packages installed in the current Python environment
    run_command(["pip", "list"])
    run_command(["pip", "show", "promptflow", "promptflow-sdk"])

    pytest_command = ["pytest", f"--junitxml={args.o}"]
    pytest_command += test_paths_list
    if args.coverage_config:
        if args.p:
            cov_path_list = [f"--cov={path}" for path in args.p]
            pytest_command += cov_path_list
        if not args.disable_cov_branch:
            pytest_command += ["--cov-branch"]
        pytest_command += [  # noqa: W503
            "--cov-report=term",
            "--cov-report=html",
            "--cov-report=xml",
        ]
        pytest_command += [f"--cov-config={args.coverage_config}"]
    if args.ignore_glob:
        pytest_command += [f"--ignore-glob={args.ignore_glob}"]
    pytest_command += [
        "-n",
        args.n,
        "--dist",
        "loadfile",
        "--log-level=info",
        "--log-format=%(asctime)s %(levelname)s %(message)s",
        "--log-date-format=[%Y-%m-%d %H:%M:%S]",
        "--durations=5",
        "-ra",
        "-vv",
    ]

    if args.timeout:
        pytest_command += [
            "--timeout",
            args.timeout,
            "--timeout_method",
            "thread",
        ]

    if args.m != "all":
        pytest_command += ["-m", args.m]

    if args.model_name:
        pytest_command += ["--model-name", args.model_name]

    # pytest --junit-xml=test-results.xml --cov=azure.ai.ml --cov-report=html --cov-report=xml -ra ./tests/*/unittests/
    error_code, _ = run_command(pytest_command, throw_on_retcode=False)
    # https://docs.pytest.org/en/7.1.x/reference/exit-codes.html
    if error_code == 1:
        print_red("Tests were collected and run but some of the tests failed.")
    elif error_code == 2:
        print_red("Test execution was interrupted by the user.")
    elif error_code == 3:
        print_red("Internal error happened while executing tests.")
    elif error_code == 4:
        print_red("pytest command line usage error.")
    elif error_code == 5:
        print_red("No tests were collected.")
    sys.exit(error_code)
