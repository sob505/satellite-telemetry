import os
import re


def find_csv_files_in_code(lines):
    csv_files = []
    csv_pattern = re.compile(r'(?:open|read_csv)\s*\(\s*[\'"]([^\'"]+\.csv)[\'"]')

    for i, line in enumerate(lines):
        match = csv_pattern.search(line)
        if match:
            csv_files.append((match.group(1), i))

    return csv_files


def check_csv_files_exist(csv_files, repo_path):
    missing_files = []

    for csv_file, line_num in csv_files:
        file_path = os.path.join(repo_path, csv_file)
        if not os.path.exists(file_path):
            missing_files.append((csv_file, line_num))

    return missing_files


def fix_missing_files(lines, missing_files, replace_with="placeholder.csv"):
    for missing_file, line_num in missing_files:
        if replace_with:
            lines[line_num] = lines[line_num].replace(missing_file, replace_with)
        else:
            lines[line_num] = ""

    return lines


def repair_generated_code(file_path, repo_path, replace_with="placeholder.csv"):
    with open(file_path, "r") as f:
        lines = f.readlines()

    csv_files = find_csv_files_in_code(lines)
    missing_files = check_csv_files_exist(csv_files, repo_path)

    if not missing_files:
        return False, "No missing CSV files found."

    updated_lines = fix_missing_files(lines, missing_files, replace_with)

    with open(file_path, "w") as f:
        f.writelines(updated_lines)

    return True, f"Fixed {len(missing_files)} missing CSV references."