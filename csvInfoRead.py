import pandas as pd
import numpy as np

def inforead(filename):
    # Reads file and takes important info into a DataFrame
    df = pd.read_csv(filename, usecols=['Carrier Name & Tracking Number'])

    # Initialize lists to store separated values
    carrier_names = []
    tracking_numbers = []

    # Process each row in the DataFrame
    for index, row in df.iterrows():
        carrier_tracking = row['Carrier Name & Tracking Number']

        # Extract carrier name (before the first parenthesis)
        if "(" in carrier_tracking:
            carrier_name = carrier_tracking.split("(")[0].strip()
        else:
            carrier_name = carrier_tracking.strip()
        carrier_names.append(carrier_name)

        # Extract tracking numbers (within parentheses, handling multiple tracking numbers)
        tracking_numbers_list = []
        while "and" in carrier_tracking:
            start = carrier_tracking.find("(") + 1
            end = carrier_tracking.find(")")
            if start < end:
                tracking_number = carrier_tracking[start:end].strip()
                tracking_numbers_list.append(tracking_number)
                carrier_tracking = carrier_tracking[carrier_tracking.find("and") + 3:].strip()
            else:
                break

        # Handle the last or single tracking number
        if "(" in carrier_tracking and ")" in carrier_tracking:
            start = carrier_tracking.find("(") + 1
            end = carrier_tracking.find(")")
            if start < end:
                tracking_number = carrier_tracking[start:end].strip()
                tracking_numbers_list.append(tracking_number)

        tracking_numbers.append(tracking_numbers_list)

    # Prepare the final array
    final_list = []
    for i in range(len(df)):
        for tn in tracking_numbers[i]:
            final_list.append([carrier_names[i], tn, i + 2])

    final = np.array(final_list)

    return final
