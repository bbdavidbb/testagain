import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# https://github.com/GSA/marketplace-fedramp-gov-data use the data.json
# is updated daily



# okta gcchigh: ['Collaboration', 'Cybersecurity & Risk Management', 'Human Resources', 'Operations Management', 'System Administration']
# okta regular: ['']
# lesson learned business category is not a good way to filter products in Fedramp


def pretty_print_json_keys(json_data, depth=0, max_depth=3):
    if depth > max_depth:
        return

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            print('  ' * depth + f'Key: {key}')
            pretty_print_json_keys(value, depth + 1, max_depth)

    elif isinstance(json_data, list):
        for index, value in enumerate(json_data):
            print('  ' * depth + f'Index: {index}')
            pretty_print_json_keys(value, depth + 1, max_depth)

def pretty_print_json(json_data):
    pretty = json.dumps(json_data, indent=2)
    print(pretty)

def explode_count_col(df, col):
    df_exploded = df.explode(col)
    count_per_category = df_exploded[col].value_counts()
    return count_per_category

def get_exploded_df(df, col, value):
    df[col] = df[col].apply(lambda x: x if x else np.nan)

    # Explode the col column into separate rows
    df_exploded = df.explode(col)
    # Drop NaN values after exploding
    df_exploded = df_exploded.dropna(subset=[col])
    df_val_only = df_exploded[df_exploded[col] == value]

    return df_val_only

def plot_business_categories(value_counts):
    num_cats = 20
    top_categories = value_counts.head(num_cats)

    dynamic_colors = plt.cm.tab20b.colors[:len(value_counts)]

    plt.figure(figsize=(13, 8))
    top_categories.plot(kind='bar', color=dynamic_colors)
    plt.title(f"Top {num_cats} Business Categories for SaaS only products in FedRamp")
    plt.xlabel('Business Categories')
    plt.ylabel('Number in each category')
    # Remove x-axis tick labels
    plt.xticks([])

    # Create legend
    legend_labels = top_categories.index
    legend_colors = [plt.cm.tab20b.colors[i] for i in range(len(legend_labels))]
    legend_counts = top_categories.values
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=f'{label} ({count})') for color, label, count in zip(legend_colors, legend_labels, legend_counts)]
    plt.legend(handles=legend_elements, title='Business Categories', loc='upper right', bbox_to_anchor=(1.2, 1))
    plt.subplots_adjust(right=0.8)
    plt.show()

with open('./data.json', 'r', encoding='UTF-8') as file:
    json_data = json.load(file)

# pretty_print_json_keys(json_data, max_depth=0)
product = json_data['data']['Products']

df = pd.DataFrame(product)
print(f"Shape of full FedRamp df: {df.shape}")
print("--------")
print(explode_count_col(df, col='service_model'))

df_saas = get_exploded_df(df, col='service_model', value = 'SaaS')
df_saas_only = df[df['service_model'].apply(lambda x: isinstance(x, list) and len(x) == 1 and x[0] == 'SaaS')]

print(f"Shape of full FedRamp SaaS only df: {df_saas_only.shape}")
print("--------")
business_fun_count = explode_count_col(df_saas_only, col='business_function')
print(business_fun_count)
print(f"Shape of business fun count: {business_fun_count.shape}")
plot_business_categories(business_fun_count)