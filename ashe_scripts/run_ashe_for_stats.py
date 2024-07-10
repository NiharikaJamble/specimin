"""
Script to run Ashe.RepositoryAutomationEngine and Specimin scripts to analyze the log file generated by ASHE in dryrun mode.
https://github.com/jonathan-m-phillips/ASHE_Automated-Software-Hardening-for-Entrypoints

Created by: Jonathan Phillips, https://github.com/jonathan-m-phillips
Date: April 13, 2024

Usage:
python3 run_ashe_for_stats.py <path_to_clone_ashe> <path_to_csv> <path_to_clone_csv_repositories> <path_to_config.properties>
"""
import subprocess
import sys
import threading
import datetime
import time
import os


def run(ashe_path: str, csv_path: str, clone_path: str, props_file_path: str):
    """
    Run ASHE and Specimin scripts to analyze the log file.
    Args:
        ashe_path: absolute path to clone the ASHE repository
        csv_path: absolute path to the CSV file containing the repositories ASHE will iterate over
        clone_path: absolute path to clone the repositories in the CSV file ASHE will iterate over
        props_file_path: absolute path to the directory containing the config.properties files for ASHE
    """

    ashe_url: str = "https://github.com/jonathan-m-phillips/ASHE_Automated-Software-Hardening-for-Entrypoints"
    # clone or update repository
    __git_clone_or_update(ashe_url, ashe_path)

    start_time: datetime = datetime.datetime.now()
    status_thread: threading.Thread = threading.Thread(target=__print_ashe_runtime, args=(start_time,))
    status_thread.daemon = True
    status_thread.start()
    __build_and_run_ashe(csv_path, clone_path, props_file_path, working_dir=ashe_path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory path: {current_dir}")
    current_dir = current_dir.replace('ASHE/ashe_scripts', 'ashe_scripts')
    main_project_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    stats_script = os.path.join(current_dir, 'specimin_statistics.py')
    rank_script = os.path.join(current_dir, 'specimin_exception_rank.py')
    print(f"Current directory path after normalising: {current_dir}")
    print(f"main project path: {main_project_dir}")
    print(f"Statistics script path: {stats_script}")
    print(f"Exception rank script path: {rank_script}")
    # run Specimin scripts
    log_path: str = os.path.join(ashe_path, "logs", "app.log")
    print("Running statistics script...")
    __run_command(f"python3 {stats_script} {log_path}")

    print("Running exception rank script...")
    __run_command(f"python3 {rank_script} {log_path}")


def __run_command(command, working_dir=None):
    try:
        result = subprocess.run(command, cwd=working_dir, shell=True, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e.stderr.decode())


def __git_clone_or_update(repo_url, ashe_path):
    """Clone or update the git repository."""
    if not os.path.exists(ashe_path):
        print("Cloning the repository...")
        __run_command(f"git clone {repo_url} {ashe_path}")
    else:
        print("Repository exists. Checking if it's a Git repository...")
        if not os.path.exists(os.path.join(ashe_path, '.git')):
            print(f"The directory {ashe_path} is not a Git repository.")
            __run_command(f"git clone {repo_url} {ashe_path}")
        else:
            print("Updating the repository...")
            os.chdir(ashe_path)
            __run_command("git pull")


def __build_and_run_ashe(csv_path: str, clone_path: str, props_file_path: str, working_dir: str):
    """Build and run the ASHE project using gradle."""
    # build ASHE
    build_command: str = './gradlew build'
    model_type: str = "dryrun"
    run_automation_command: str = f"./gradlew runRepositoryAutomation -PrepositoriesCsvPath=\"{csv_path}\" -PcloneDirectory=\"{clone_path}\" -Pllm=\"{model_type}\" -PpropsFilePath=\"{props_file_path}\""

    print("Building ASHE...")
    __run_command(build_command, working_dir=working_dir)

    print("Running ASHE...")
    __run_command(run_automation_command, working_dir=working_dir)


def __print_ashe_runtime(start_time):
    """Function to print the elapsed time since ASHE started."""
    print("ASHE started.")
    print("ASHE runtime: 00:00:00")
    while True:
        time.sleep(300)  # sleep for 5 minute
        elapsed_time = datetime.datetime.now() - start_time
        # format elapsed time into H:M:S
        formatted_time = str(elapsed_time).split('.')[0]  # remove microseconds
        print(f"ASHE runtime: {formatted_time}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 run_ashe_for_stats.py <path_to_clone_ashe> <path_to_csv> <path_to_clone_csv_repositories> <path_to_config.properties>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
