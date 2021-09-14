import argparse
import csv
import datetime
import os
import statistics
import time
import urllib.parse

import requests
import teamscale_client.data
from teamscale_client.teamscale_client_config import TeamscaleClientConfig
from teamscale_precommit_client import PrecommitClient


def run_precommit(args):
    teamscale_config = TeamscaleClientConfig.from_config_file(
        os.path.join(args.precommit_project_folder, ".teamscale-precommit.config"))
    precommit_client = PrecommitClient(teamscale_config, args.precommit_project_folder)
    precommit_client.run()


def get_findings_churn(args):
    url = urllib.parse.urljoin(args.teamscale_url,
                               "/api/projects/{0}/merge-requests/finding-churn".format(args.teamscale_project))
    url_parts = list(urllib.parse.urlparse(url))
    query = {"source": args.merge_source, "target": args.merge_target}
    url_parts[4] = urllib.parse.urlencode(query)
    url = urllib.parse.urlunparse(url_parts)

    requests.get(url, auth=(args.teamscale_user, args.teamscale_access_key))


def get_findings_perspective(args):
    url = urllib.parse.urljoin(args.teamscale_url,
                               "/api/projects/{0}/findings/list/with-count".format(args.teamscale_project))
    url_parts = list(urllib.parse.urlparse(url))
    query = {"all": True}
    url_parts[4] = urllib.parse.urlencode(query)
    url = urllib.parse.urlunparse(url_parts)

    requests.get(url, auth=(args.teamscale_user, args.teamscale_access_key))


def run_benchmark(benchmark_function, args):
    measurements = []
    test_run = 1
    start_all = datetime.datetime.now()
    while len(measurements) < 10:
        print("Running {0} for the {1} time".format(benchmark_function.__name__, test_run))
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

    end_all = datetime.datetime.now()

    additional_metrics = [statistics.mean(measurements), statistics.median(measurements)]
    results = ["{0}".format(benchmark_function.__name__)] + \
              ["{0}".format(start_all.timestamp()), "{0}".format(start_all)] + \
              ["{0}".format(end_all.timestamp()), "{0}".format(end_all)] + \
              list(map(lambda value: "{:10.20f}".format(value), additional_metrics)) + \
              list(map(lambda value: "{:10.20f}".format(value), measurements))

    return results


def write_csv_row(file, row):
    writer = csv.writer(file)
    writer.writerow(row)


def generate_csv_header():
    header = ["benchmark_name", "start_timestamp", "start_time", "end_timestamp", "end_time", "mean", "median"]
    for i in range(1, 11):
        header.append("measurement_{0}".format(i))
    return header


def run_all_benchmarks(args):
    with open("teamscale-benchmark-results.csv", mode="w") as csv_file:
        write_csv_row(csv_file, generate_csv_header())

        if os.path.isdir(args.precommit_project_folder):
            print("Running precommit benchmark...")
            precommit_results = run_benchmark(run_precommit, args)
            write_csv_row(csv_file, precommit_results)
        else:
            print("Could not find pre-commit folder '{0}'".format(args.precommit_project_folder))

        print("Running findings churn benchmark...")
        findings_churn_results = run_benchmark(get_findings_churn, args)
        write_csv_row(csv_file, findings_churn_results)

        print("Running findings perspective benchmark...")
        findings_perspective_results = run_benchmark(get_findings_perspective, args)
        write_csv_row(csv_file, findings_perspective_results)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("teamscale_url")
    arg_parser.add_argument("teamscale_user")
    arg_parser.add_argument("teamscale_access_key")
    arg_parser.add_argument("precommit_project_folder")
    arg_parser.add_argument("teamscale_project")
    arg_parser.add_argument("merge_source")
    arg_parser.add_argument("merge_target")
    args = arg_parser.parse_args()

    run_all_benchmarks(args)


if __name__ == "__main__":
    main()
