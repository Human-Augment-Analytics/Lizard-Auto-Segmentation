# Written Using ChatGPT 3.5

import chardet
import csv

def detect_encoding(filename):
    with open(filename, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def calculate_contributions(filename):
    user_stats = {}
    total_changes = 0

    encoding = detect_encoding(filename)
    print(f"Detected encoding: {encoding}")

    try:
        with open(filename, 'r', encoding=encoding) as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(': ', 1)
                    if len(parts) == 2:
                        user = parts[0]
                        stats = parts[1].split(', ')
                        if len(stats) == 4:
                            try:
                                total_changes_user = int(stats[3].split(' ')[0])
                                
                                if user in user_stats:
                                    user_stats[user] += total_changes_user
                                else:
                                    user_stats[user] = total_changes_user
                                
                                total_changes += total_changes_user
                            except ValueError:
                                print(f"Skipping line with invalid number format: {line}")
                        else:
                            print(f"Skipping line with unexpected stats format: {line}")
                    else:
                        print(f"Skipping line with unexpected format: {line}")
                else:
                    print("Skipping empty line")
    except FileNotFoundError:
        print(f"File {filename} not found")
        return

    if total_changes == 0:
        print("No changes found")
        return

    # Sort user_stats by percentage of total changes in descending order
    sorted_stats = sorted(user_stats.items(), key=lambda x: x[1] / total_changes, reverse=True)

    # Write the output to a new CSV file
    with open('calculated-contributions.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['User', 'Total Changes', 'Percentage of Total'])
        for user, changes in sorted_stats:
            percentage = (changes / total_changes) * 100
            csv_writer.writerow([user, changes, f"{percentage:.2f}%"])

    print("Output written to calculated-contributions.csv")

# Call the function with the filename
calculate_contributions('git-stats-output.txt')