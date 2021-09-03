#!/usr/bin/env sh

function run_precommit() {
	# TODO
	echo precommit
}

function get_findings_churn() {
	# TODO
	echo finding churn
}

function get_findings_perspecitve() {
	# TODO
	echo findings perspective
}

function run_benchmark() {
	# TODO Run the above functions (provided as argument) 10 times and output times needed for each, average, worst, best. Maybe write into csv.
	benchmark_function=$1
	$benchmark_function
}

function run_all_benchmarks() {
	run_benchmark run_precommit
	run_benchmark get_findings_churn
	run_benchmark get_findings_perspecitve
}


positional=()

# Parse arguments
while [[ $# -gt 0 ]]; do
	key="$1"
	case $key in
		* )
			positional+=("$1")
			shift
			;;
	esac
done

if [[ "${#positional[@]}" -lt 3 ]]; then
	echo Missing argument: teamscale-benchmark.sh TEAMSCALE_URL USER ACCESS_KEY
	exit
fi

url=${positional[0]}
user=${positional[1]}
access_key=${positional[2]}

run_all_benchmarks
