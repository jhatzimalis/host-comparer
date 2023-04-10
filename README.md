# Host-Comparer

Compare lists of domains and IP addresses to find: All data, similarities, and differences. Output using newlines or commas.

## Setup
--------------------------------------------------
    Step 0: Place 2 or more log directories in 'logs\'.
        - Give unique identifiable names to each directory
        - Each directory can contain 1 or more tsv data files.
            - The data files should have domains in the first column, and ip addresses in the second column.

    Step 0.5: Run 'main.py'.
        - From project root

## Runtime Options
--------------------------------------------------
    Step 1: Choose old and new directories.
        - Enter the ID associated with the OLD logs, click Enter, Enter the ID associated with the NEW logs, click Enter

    Step 2: Choose option - Include Domains (1), IPs (2), or Both (3)? 
        - Enter ID of option (Default: Both)

    Step 3: Choose option - Include All Old/New Data (1), Similarities (2), Differences (3), or Everything (4)?
        - Enter 1 or more option IDs (Default: Everything)
            - The options can be seperated in any way, or not seperated at all. The input is saved as a string and single digit integers are extracted
    
    Step 4: Choose option - Seperate values using Newline (1), or Comma (2)?
        - Enter ID of option (Default: Newline)

    Step 5: The output will be written to a text file. This file can be located in the 'output/' directory.
        - File name will be: old_folder_name + "_" + new_folder_name + ".txt"





