import argparse


def run_precommit():
    # TODO
    print("precommit")


def get_findings_churn():
    # TODO
    print("finding churn")


def get_findings_perspective():
    # TODO
    print("findings perspective")


def run_benchmark(benchmark_function):
    # TODO Run the above defs (provided as argument) 10 times and output times needed for each, average, worst, best. Maybe write into csv.
    benchmark_function()


def run_all_benchmarks():
    print("Running precommit benchmark...")
    run_benchmark(run_precommit)
    print("Running findings churn benchmark...")
    run_benchmark(get_findings_churn)
    print("Running findings perspective benchmark...")
    run_benchmark(get_findings_perspective)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("teamscale_url")
    arg_parser.add_argument("teamscale_user")
    arg_parser.add_argument("teamscale_access_key")
    args = arg_parser.parse_args()

    run_all_benchmarks()


if __name__ == "__main__":
    main()
