"""
Script for analyzing log files generated by ASHE in dryrun mode.
https://github.com/jonathan-m-phillips/ASHE_Automated-Software-Hardening-for-Entrypoints

Created by: Jonathan Phillips, https://github.com/jonathan-m-phillips
Date: April 13, 2024

Description:
This script reads a log file and computes attempted, successful, and failed Specimin minimization
and compilation statistics. These statistics come from running the Ashe.RepositoryAutomationEngine
in dryrun mode.

Output:
Summary written to a txt file in the same directory as the provided log file.

Usage:
python3 specimin_statistics.py <path_to_log_file.log>
"""

import sys
import os
import re


def analyze_log(file_path: str):
    directory: str = os.path.dirname(file_path)
    output_file_path: str = os.path.join(directory, 'specimin_statistics.txt')

    with open(output_file_path, 'w') as output_file:
        with open(file_path, 'r') as file:
            lines: list[str] = file.readlines()

        repo_stats: dict[str, int] = {
            'minimization_attempts': 0,
            'successful_minimization': 0,
            'failed_minimization': 0,
            'compilation_attempts': 0,
            'successful_compilation': 0,
            'failed_compilation': 0,
            'full_success': 0
        }
        repo_path: str = ""
        branch_name: str = ""

        for line in lines:
            line: str = line.strip()

            # get the repository path and branch name from the log line
            if "Processing repository at:" in line:
                # if Ashe Repository Automation Engine finished processing a repository
                # and moved on to the next repository, print and reset the statistics
                if repo_path:
                    __print_and_write_stats(repo_stats, repo_path, branch_name, output_file)
                    repo_stats = repo_stats.fromkeys(repo_stats, 0)

                repo_path, branch_name = __extract_repo_and_branch(line)

            __update_stats(line, repo_stats)

            if "Completed processing repository at:" in line:
                __print_and_write_stats(repo_stats, repo_path, branch_name, output_file)
                repo_stats = repo_stats.fromkeys(repo_stats, 0)  # reset statistics for new repo
    print("Write successful")


def __update_stats(line, repo_stats):
    if "Minimizing source file..." in line:
        repo_stats['minimization_attempts'] += 1
    if "BUILD SUCCESSFUL" in line:
        repo_stats['successful_minimization'] += 1
    if "BUILD FAILED" in line:
        repo_stats['failed_minimization'] += 1
    if "Compiling Java files" in line:
        repo_stats['compilation_attempts'] += 1
    if "Minimized files compiled successfully." in line:
        repo_stats['successful_compilation'] += 1
        repo_stats['full_success'] += 1
    if "Minimized files failed to compile." in line:
        repo_stats['failed_compilation'] += 1


def __print_and_write_stats(stats, repo_path, branch_name, output_file):
    successful_min_percent = (stats['successful_minimization'] / stats['minimization_attempts'] * 100) if stats[
        'minimization_attempts'] else 0
    failed_min_percent = (stats['failed_minimization'] / stats['minimization_attempts'] * 100) if stats[
        'minimization_attempts'] else 0
    successful_comp_percent = (stats['successful_compilation'] / stats['compilation_attempts'] * 100) if stats[
        'compilation_attempts'] else 0
    failed_comp_percent = (stats['failed_compilation'] / stats['compilation_attempts'] * 100) if stats[
        'compilation_attempts'] else 0
    full_success_percent = (stats['full_success'] / stats['minimization_attempts'] * 100) if stats[
        'minimization_attempts'] else 0

    output_content = f"""
Running Specimin on repository: {repo_path} for branch: {branch_name}
Attempted minimization - {stats['minimization_attempts']}:
Successfully minimized {stats['successful_minimization']} ({successful_min_percent:.2f}%) target methods.
Failed to minimize {stats['failed_minimization']} ({failed_min_percent:.2f}%) target methods.

Attempted compilation - {stats['compilation_attempts']}:
Successful: {stats['successful_compilation']} ({successful_comp_percent:.2f}%)
Failed: {stats['failed_compilation']} ({failed_comp_percent:.2f}%)

Fully successful from minimization to compilation: {stats['full_success']} ({full_success_percent:.2f}%)

"""
    output_file.write(output_content)


def __extract_repo_and_branch(log_line: str):
    """
    Extracts the repository path and branch name from a log line.

    Parameters:
    - log_line (str): A string from the log file containing repository and branch information.

    Returns:
    - tuple: A tuple containing the repository path and the branch name.
    """
    # regex pattern to find the repository path and branch name
    pattern = r"Processing repository at: (.+?) for branch: (.+)"
    match = re.search(pattern, log_line)

    if match:
        repo_path = match.group(1).strip()
        branch_name = match.group(2).strip()
        return repo_path, branch_name
    else:
        return "", ""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 specimin_statistics.py <path_to_log_file.log>")
        sys.exit(1)
    log_file_path = sys.argv[1]
    analyze_log(log_file_path)
