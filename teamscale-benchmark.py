import argparse
import os

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
    # TODO Run the above defs (provided as argument) 10 times and output times needed for each, average, worst, best. Maybe write into csv.
    benchmark_function(args)


def run_all_benchmarks(args):
    print("Running precommit benchmark...")
    run_benchmark(run_precommit, args)
    print("Running findings churn benchmark...")
    run_benchmark(get_findings_churn, args)
    print("Running findings perspective benchmark...")
    run_benchmark(get_findings_perspective, args)


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
