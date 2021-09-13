import argparse
import os
import statistics
import time

import teamscale_client.data
from teamscale_client.teamscale_client_config import TeamscaleClientConfig
from teamscale_precommit_client import PrecommitClient


def run_precommit(args):
    teamscale_config = TeamscaleClientConfig.from_config_file(
        os.path.join(args.precommit_project_folder, ".teamscale-precommit.config"))
    precommit_client = PrecommitClient(teamscale_config, "./precommit")
    precommit_client.run()


def get_findings_churn(args):
    # TODO
    print("finding churn")


def get_findings_perspective(args):
    # TODO
    print("findings perspective")


def run_benchmark(benchmark_function, args):
    measurements = []
    test_run = 1
    while len(measurements) < 10:
        print("Running {0} for the {1} time:".format(benchmark_function.__name__, test_run))
        try:
            start = time.time()
            benchmark_function(args)
            end = time.time()
            benchmark_time = end - start
            measurements.append(benchmark_time)
            test_run = test_run + 1
        except teamscale_client.data.ServiceError:
            print("Pre-commit ran two fast back to back, retrying test run {0}".format(test_run))
            time.sleep(5)

    additional_metrics = [statistics.mean(measurements), statistics.median(measurements)]
    results = ["{0}".format(benchmark_function.__name__)] + \
              list(map(lambda value: "{0}".format(value), additional_metrics)) + \
              list(map(lambda value: "{0}".format(value), measurements))
    return results


def write_csv_row(row):
    # TODO
    return


def generate_csv_header():
    header = ["benchmark_name", "mean", "median"]
    for i in range(1, 11):
        header.append("measurement_{0}".format(i))
    return header


def run_all_benchmarks(args):
    write_csv_row(generate_csv_header())

    print("Running precommit benchmark...")
    precommit_results = run_benchmark(run_precommit, args)
    write_csv_row(precommit_results)

    print("Running findings churn benchmark...")
    findings_churn_results = run_benchmark(get_findings_churn, args)
    write_csv_row(findings_churn_results)

    print("Running findings perspective benchmark...")
    findings_perspective_results = run_benchmark(get_findings_perspective, args)
    write_csv_row(findings_perspective_results)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("teamscale_url")
    arg_parser.add_argument("teamscale_user")
    arg_parser.add_argument("teamscale_access_key")
    arg_parser.add_argument("teamscale_project")
    arg_parser.add_argument("precommit_project_folder")
    args = arg_parser.parse_args()

    run_all_benchmarks(args)


if __name__ == "__main__":
    main()
