import argparse
import csv
import datetime
import multiprocessing
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


def get_server_status(args):
    url = urllib.parse.urljoin(args.teamscale_url, "/api/execution-status/workers")
    response = requests.get(url, auth=(args.teamscale_user, args.teamscale_access_key))

    number_of_active_workers = sum(1 for x in response.json()[0]["workers"] if "taskName" in x)
    job_queue_size = response.json()[0]["jobQueueSize"]

    return number_of_active_workers, job_queue_size


def try_running_benchmark(benchmark_function, args, measurements):
    try:
        start = time.time()
        benchmark_function(args)
        end = time.time()
        benchmark_time = end - start
        measurements.append(benchmark_time)

    except teamscale_client.data.ServiceError:
        print("Pre-commit ran two fast back to back, retrying test run {0}".format(len(measurements) + 1))
        time.sleep(5)


def run_benchmark(benchmark_function, args):
    with multiprocessing.Manager() as manager:
        timeout = 20 * 60  # 20 Minutes
        measurements = manager.list()
        start_all = datetime.datetime.now()
        number_of_active_workers = -1
        job_queue_size = -1
        while len(measurements) < 10:
            (number_of_active_workers, job_queue_size) = get_server_status(args)
            print("Running {0} for the {1} time".format(benchmark_function.__name__, len(measurements) + 1))

            # https://stackoverflow.com/questions/492519/timeout-on-a-function-call
            process = multiprocessing.Process(target=try_running_benchmark,
                                              args=(benchmark_function, args, measurements))
            process.start()
            process.join(timeout)

            if process.is_alive():
                process.terminate()
                process.join()
                break

        end_all = datetime.datetime.now()

        additional_metrics = ["", "", "", ""]
        if len(measurements) > 0:
            additional_metrics = ["{:10.20f}".format(statistics.mean(measurements)),
                                  "{:10.20f}".format(statistics.median(measurements)),
                                  "{:10.20f}".format(max(measurements)),
                                  "{:10.20f}".format(min(measurements))]

        results = ["{0}".format(benchmark_function.__name__)] + \
                  ["{0}".format(start_all.timestamp()), "{0}".format(start_all)] + \
                  ["{0}".format(end_all.timestamp()), "{0}".format(end_all)] + \
                  ["{0}".format(number_of_active_workers), "{0}".format(job_queue_size)] + \
                  additional_metrics + \
                  list(map(lambda value: "{:10.20f}".format(value), measurements))

        return results


def write_csv_row(file, row):
    writer = csv.writer(file)
    writer.writerow(row)


def generate_csv_header():
    header = ["benchmark_name", "start_timestamp", "start_time", "end_timestamp", "end_time",
              "number_of_active_workers", "job_queue_size", "mean", "median", "max", "min"]
    for i in range(1, 11):
        header.append("measurement_{0}".format(i))
    return header


def run_all_benchmarks(args):
    benchmark_results_file = "./teamscale-benchmark-results.csv"
    if not os.path.isfile(benchmark_results_file):
        with open(benchmark_results_file, mode="w") as csv_file:
            write_csv_row(csv_file, generate_csv_header())

    with open(benchmark_results_file, mode="a") as csv_file:
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
