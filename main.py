import os
from datetime import datetime


def getLogs(logs_dir):
    """
    Creates a list of directories in 'Logs/', then prints them with a respective ID.
    Args: logs_dir (str) - The directory that logs should be stored in
    Returns: List of parent directories
    """
    try:
        # List all files and directories in the specified directory and filter to only include directories
        dirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
        if not dirs:
            # TEST THIS
            raise ValueError("No child directories found in logs/ folder")
    except OSError as e:
        print(f"Error occurred when finding child directories of logs/: {e}")
        exit()

    # Print log directories with respective ID
    print("Available log directories:")
    for i, option in enumerate(dirs):
        print(f"{i+1}: {option}")

    return dirs


def chooseLogs(options, prompts):
    """
    This function prompts the user to choose IDs for old and new data from a list of directories and returns a tuple of their chosen options.
    Args: options (list) - a list of strings representing the available options for the user to choose from. prompts (list): a list of strings representing prompts to be displayed to the user for each option.
    Returns: A tuple of integers representing the options chosen by the user.
    """
    choices = []
    # Loop through each prompt
    for prompt in prompts:
        while True:
            try:
                choice = int(input(prompt))
                if choice < 1 or choice > len(options):
                    raise ValueError
                index = choice - 1
                if options[index] in choices:
                    print("You have already chosen this option. Please choose another.")
                else:
                    choices.append(options[index])
                    break
            except ValueError:
                print(
                    f"Invalid input. Please enter an integer between 1 and {len(options)}")
                
    return tuple(choices)


def get_data_file_paths(dir_path, file_ext):
    """
    Use os.walk to find all files with the desired file extension
    Args: dir_path (str) - full path of directory in 'logs/'. file_ext (str) - allowed file extension
    Returns: List of strings containing data file paths within dir_path parent directory.
    """
    data_files = []
    try:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(file_ext):
                    data_files.append(os.path.join(root, file))
    except:
        print("An error occured while finding data files.")

    return data_files


def sort_ips(ips):
    """
    Sorts a list of IP addresses, sorts the IPv4 addresses as integers, and appends the sorted IPv6 addresses to the sorted IPv4 addresses.
    Args: ips (list) - a list of IP addresses
    Returns: List of sorted IP addresses
    """
    # Split IP addresses into IPv4 and IPv6 addresses
    ipv4_addrs = []
    ipv6_addrs = []
    for ip in ips:
        # Check if the IP address contains a dot (for IPv4) or not (for IPv6)
        if '.' in ip:
            ipv4_addrs.append(ip)
        else:
            ipv6_addrs.append(ip)

    # Sort IPv4 addresses as integers and append sorted IPv6 addresses
    sorted_ipv4 = sorted(ipv4_addrs, key=lambda x: [int(i) for i in x.split('.')])
    sorted_ipv6 = sorted(ipv6_addrs)
    sorted_ips = sorted_ipv4 + sorted_ipv6

    return sorted_ips


def sort_dict(dictionary):
    """
    Sorts the values in a dictionary and creates a new dictionary with sorted values.
    Args: dictionary (dict) - a dictionary whose values need to be sorted
    Returns: Dict with sorted values
    """
    # Sort each list in the dictionary and create a new dictionary with sorted lists
    sorted_dict = {}
    for key, value in dictionary.items():
        # If the key contains "ip" in any case, call the sort_ips function to sort its values accurately 
        if 'ip' in key.lower():
            sorted_dict[key] = sort_ips(value)
        else:
            # Sort the list of values regularly and add it to the sorted_dict
            sorted_dict[key] = sorted(value)

    return sorted_dict


def read_data_files(old_paths, new_paths):
    """
    Reads data files and extracts domains and IPs from first two columns. Creates sorted dict of extracted values.
    Args: old_paths (list) - a list of strings representing paths to old data files. new_paths (list) - a list of strings representing paths to new data files
    Returns: Dict of sorted domains and ips from old and new data files 
    """
    domains = {"old": set(), "new": set()}
    ips = {"old": set(), "new": set()}

    # Unwanted values that will be removed (eg. headers, empty values)
    unwanted_values = {"Name", "IP", "N/A"}

    for paths, dataset_type in ((old_paths, "old"), (new_paths, "new")):
        for path in paths:
            # For each data file
            try:
                with open(path, 'r') as f:
                    for line in f:
                        # Split the line into fields
                        fields = line.strip().split('\t')
                        # Extract the domain and IP from fields
                        domain, ip = fields[:2]
                        # Add the domain to domains set if it's not in unwanted_values
                        if domain not in unwanted_values:
                            domains[dataset_type].add(domain)
                        # Split IP into individual IPs, strip unwanted characters, and add them to ips set
                        for i in ip.strip('[]\"').split(','):
                            if i not in unwanted_values:
                                ips[dataset_type].add(i.strip())
            except Exception as e:
                print(f"*WARNING* POSSIBLE DATA LOSS - Error occurred when reading {path}: {e}")

    # Create and sort dict
    data = {"old_domains": domains["old"], "old_ips": ips["old"],
            "new_domains": domains["new"], "new_ips": ips["new"]}
    sortedResults = sort_dict(data)

    return sortedResults


def getResults(data):
    """
    Compares domains and IPs between old and new data files, and returns results of the comparison.
    Args: data (dict) - A dictionary containing sorted domains and IPs from old and new data files.
    Returns: Dict of sorted set resulting from the comparison
    """
    results = {}
    results["old_domains_not_in_new_domains"] = set(data["old_domains"]) - set(data["new_domains"])
    results["new_domains_not_in_old_domains"] = set(data["new_domains"]) - set(data["old_domains"])
    results["old_ips_not_in_new_ips"] = set(data["old_ips"]) - set(data["new_ips"])
    results["new_ips_not_in_old_ips"] = set(data["new_ips"]) - set(data["old_ips"])
    results["consistent_domains"] = set(data["new_domains"]) & set(data["old_domains"])
    results["consistent_ips"] = set(data["new_ips"]) & set(data["old_ips"])

    # Sort results
    sortedResults = sort_dict(results)

    return sortedResults


def create_formatted_data(paths, data, results):
    """
    Create a formatted dict based on the user's choices.
    Args: paths (dict) - contains old and new directories and files. data (dict) - contains all new and old data. results (dict) - contains comparison data
    Returns: Dict of formatted data that includes what should be printed
    """
    # Loop through both inputs until valid inputs are given
    while True:
        try:
            # Input 1 - Include domains and/or IPs, default to both
            option1_input = input("\nInclude Domains (1), IPs (2), or Both (3)?\nEnter ID (Default: Both) > ")

            # If user input '3 '(Both) or did not specify any option, select default options. Elif user input valid option, convert to list of integers. Else raise ValueError
            if option1_input in ['3', '']:
                option1 = [1, 2]
            elif option1_input in ['1', '2']:
                option1 = [int(option1_input)]
            else:
                raise ValueError

            while True:
                try:
                    # Input 2 - Include All Old/New Data, Similarities, Differences, or Everything, default to Everything
                    option2_input = input("\nInclude All Old/New Data (1), Similarities (2), Differences (3), or Everything (4)?\nEnter 1 or more IDs (Default: Everything) > ")
                    # Extract single digits from input string, save as list of integers. Sort to maintain proper order of input options
                    option2 = sorted([int(c) for c in option2_input if c.isdigit()])

                    # If user input '4' or did not specify any option, select default options.
                    if len(option2) == 0 or 4 in option2:
                        option2 = [1, 2, 3]

                    # If any of the chosen options are not valid, raise ValueError
                    if not all(o in [1, 2, 3] for o in option2):
                        raise ValueError
                    break
                except ValueError:
                    # ValueError for option2
                    print("Invalid input. Please enter one or more valid IDs, or click Enter for default.")
            break
        except ValueError:
            # ValueError for option1
            print("Invalid input. Please enter valid ID, or click Enter for default.")

    # Remove "logs\\" from file paths
    old_data_files = [f[5:] for f in paths["oldFilePaths"]]
    new_data_files = [f[5:] for f in paths["newFilePaths"]]

    # Create printable output representing chosen options from option1 and option2 inputs
    options1_strings = ["Domains", "IPs"]
    option1_str = " and ".join(options1_strings[num-1] for num in option1)

    options2_strings = ["All Old/New Data", "Similarities", "Differences"]
    option2_str = ", ".join(options2_strings[num-1] for num in option2)

    options_chosen = f"{option1_str} ({option2_str})"
    print("\nOutputting:", options_chosen)

    # Build dictionary based on user input
    formatted_data = {
        "Summary": {
            "Timestamp": datetime.now().strftime("%B %d, %Y at %I:%M:%S %p"),
            "Old Folder": f"{paths['oldLogName']} - Data Files: {old_data_files}",
            "New Folder": f"{paths['newLogName']} - Data Files: {new_data_files}",
            "Output": options_chosen
        },
    }

    # Only include data if the user has chosen to include it
    # If option2 includes 1, grab All Data. If option2 includes 2, grab Similarities. If option2 includes 3, grab Differences.
    # If option1 includes 1, grab Domains. If option1 includes 2, grab IPs
    if 1 in option2:
        formatted_data["All Data"] = {}
        if 1 in option1:
            formatted_data["All Data"]["Old Domains"] = data["old_domains"]
            formatted_data["All Data"]["New Domains"] = data["new_domains"]
        if 2 in option1:
            formatted_data["All Data"]["Old IPs"] = data["old_ips"]
            formatted_data["All Data"]["New IPs"] = data["new_ips"]
    if 2 in option2:
        formatted_data["Similarities"] = {}
        if 1 in option1:
            formatted_data["Similarities"]["Consistent Domains"] = results["consistent_domains"]
        if 2 in option1:
            formatted_data["Similarities"]["Consistent IPs"] = results["consistent_ips"]
    if 3 in option2:
        formatted_data["Differences"] = {}
        if 1 in option1:
            formatted_data["Differences"]["Domains Only in Old"] = results["old_domains_not_in_new_domains"]
            formatted_data["Differences"]["Domains Only in New"] = results["new_domains_not_in_old_domains"]
        if 2 in option1:
            formatted_data["Differences"]["IPs Only in Old"] = results["old_ips_not_in_new_ips"]
            formatted_data["Differences"]["IPs Only in New"] = results["new_ips_not_in_old_ips"]

    # Create a Table of Contents based on the newly created formatted_data dict
    table_of_contents = " | ".join([f"{key} - {' , '.join(formatted_data[key].keys())}" for key in formatted_data.keys() if key != "Summary"])
    formatted_data["Summary"]["Table of Contents"] = table_of_contents
    
    return formatted_data


def write_to_text(file_path, formatted_data):
    """
    Writes formatted data to a text file specified by the given file path. The function prompts the user to choose between newline and comma separators when writing the data to the file.
    Args: file_path (str) - a string specifying the path of the text file to create. formatted_data (dict) - a dictionary containing the formatted data to write to the file
    Returns: None
    """
    while True:
        try:
            # Input - Use seperator Newline or Comma, default to Newline
            output_sep_input = input("\nSeperate values using Newline (1), or Comma (2)?\nEnter ID (Default: Newline) > ")

            # If user input '1' or did not specify any option, select default option. Elif user input '2', seperator is comma. Else, raise ValueError
            if output_sep_input in ['1', '']:
                output_sep = 1
            elif output_sep_input == '2':
                output_sep = 2
            else:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter valid ID, or click Enter for default.")
    
    # Write to text file
    with open(file_path, "w") as file:
        # Iterate over the dictionary
        for section, data_dict in formatted_data.items():
            if section == "Summary":
                # Print the header differently
                file.write("~" * 50 + "\n")
                file.write("Summary:\n")
                for key, value in data_dict.items():
                    file.write(f"{key}: {value}\n")
                file.write("~" * 50 + "\n\n")
                continue  # Skip printing the "Logs" section again

            # Print data for other sections
            file.write(f"{'=' * 50}\n{section}\n{'=' * 50}")
            for key, value in data_dict.items():
                if output_sep == 2:
                    # -- Print with commas --
                    items_str = ", ".join(value)
                    file.write(f"\n{key} ({len(value)})\n{'-' * 50}\n")
                    file.write(f"{items_str}\n")
                else:
                    # -- Print with newlines --
                    file.write(f"\n{key} ({len(value)})\n{'-' * 50}\n")
                    for item in value:
                        file.write(f"{item}\n")
            file.write("\n")
    # Print final message after file has been written indicating its path
    print("\nText file created:", file_path)


if __name__ == '__main__':
    # Log directories location
    logs_path = 'logs'
    
    # Allowed file ext
    file_ext = '.tsv'

    # dict storing directory and file paths
    paths = {}

    # Returns a list of all log paths that the user will be able to choose form
    paths["logParents"] = getLogs(logs_path)

    # Get valid input for the old and new log directories. Returns old directory name and new directory name
    prompts = ["Enter ID of OLD logs > ", "Enter ID of NEW logs > "]
    paths["oldLogName"], paths["newLogName"] = chooseLogs(paths["logParents"], prompts)

    # Returns list of data file paths
    paths["oldFilePaths"] = get_data_file_paths(os.path.join(logs_path, paths["oldLogName"]), file_ext)
    paths["newFilePaths"] = get_data_file_paths(os.path.join(logs_path, paths["newLogName"]), file_ext)

    # Returns domains and IP addresses for old and new data files, multiple files within old/new directories respectively are combined
    data = read_data_files(paths["oldFilePaths"], paths["newFilePaths"])

    # Returns dict of comparison results
    results = getResults(data)

    # Returns dict of formatted data including only what the user has specified
    formatted_data = create_formatted_data(paths, data, results)

    # Specify output location and file name for text file
    output_path = 'output'
    output_file_name = paths["oldLogName"] + "_" + paths["newLogName"] + ".txt"
    output_file_location = os.path.join(output_path, output_file_name)
    # Write to text file
    write_to_text(output_file_location, formatted_data)
