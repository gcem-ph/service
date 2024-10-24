from collections import defaultdict
import random

def chart_js_stacked_bar(data):

    # data = [
    #     {'microscope': 'Krios 1', 'downtime': 'down', 'time': 696.0},
    #     {'microscope': 'Krios 1', 'downtime': 'up-with-issues', 'time': 576.0},
    #     {'microscope': 'Krios 2', 'downtime': 'down', 'time': 144.0},
    #     {'microscope': 'Krios 2', 'downtime': 'up-with-issues', 'time': 48.0}
    # ]

    # Step 1: Create a defaultdict to organize data by microscope and downtime
    grouped_data = defaultdict(lambda: {'down': 0, 'up-with-issues': 0})

    # Populate the grouped data

    to_list_data = list(data)
    
    for entry in to_list_data:
        microscope = entry['microscope']
        downtime = entry['downtime']
        time = entry['time']
        grouped_data[microscope][downtime] = time

    # Step 2: Extract labels (microscope names)
    labels = list(grouped_data.keys())

    # Step 3: Extract data for each downtime type
    down_data = [grouped_data[microscope]['down'] for microscope in labels]
    up_with_issues_data = [grouped_data[microscope]['up-with-issues'] for microscope in labels]

    # Step 4: Create the Chart.js structure
    chart_js_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'down',
                'data': down_data,
                'backgroundColor': random_rgba(),
                'borderWidth': 1
            },
            {
                'label': 'up-with-issues',
                'data': up_with_issues_data,
                'backgroundColor': random_rgba(),
                'borderWidth': 1
            }
        ]
    }

    return chart_js_data

def random_rgba():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgba({r}, {g}, {b}, 0.5)'

def convert_to_stacked_grouped_data(data):
    # Initialize containers for the chart.js data structure
    labels = []
    dataset_dict = {}
    color_dict = {}  # To store unique colors for each key

    # Iterate through each data point

    list_data=list(data)
    for entry in list_data:
        microscope = entry['microscope']
        downtime = entry['downtime']
        part = entry['part']
        time = entry['time']

        # Add microscope to labels if not already present
        if microscope not in labels:
            labels.append(microscope)
            
            # Ensure all existing dataset lists in dataset_dict are updated to match the new length of labels
            for key in dataset_dict:
                dataset_dict[key].append(0)

        # Create a key for each unique downtime and part combination
        key = f"{downtime} ({part})"

        # If the key doesn't exist in the dataset_dict, initialize it with an array of zeros
        if key not in dataset_dict:
            dataset_dict[key] = [0] * len(labels)

        # Find the index of the microscope and update the corresponding downtime value
        idx = labels.index(microscope)
        dataset_dict[key][idx] = time

        # Assign a unique color to each key if not already assigned
        if key not in color_dict:
            color_dict[key] = random_rgba()

    # Convert the dataset_dict into Chart.js format (datasets)
    datasets = []
    for label, values in dataset_dict.items():
        
        # Automatically derive the stack name from the part
        part = label.split(' (')[1].strip(')')  # Extract part from the label
        stack_name = part.replace(' ', '-')  # Replace spaces with hyphens for stack name

        dataset = {
            'label': label,
            'data': values,
            'backgroundColor': color_dict[label],  # Customize this if needed
            'stack': stack_name
        }

        datasets.append(dataset)

    # Return the chart.js data format
    return {
        'labels': labels,
        'datasets': datasets
    }
