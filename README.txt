DESCRIPTION

"Net Value" is a visualization tool for analyzing soccer player statistics built for the CSE 6242 Data & Visual Analytics Project. This package contains three sets of codes: data collection and processing, clustering analysis, and dash app.

Data Collection & Processing:
- soccer_data.ipynb: Collects data from the Football API using Python's requests module and pre-processes the data for future analysis (saved to a .csv file). Uses functions defined in player_stats.py to connect with, modify, and save data from the API in .json files for later use. Loads player data and removes rows with missing values in vital columns (such as total passes and total saves). Transforms player data to per match stats (per 90min).

Clustering Analysis:
- clustering_model.ipynb: Performs clustering analysis on pre_processed data and outputs the following: cluster_analysis.xlsx (Excel file with percent counts of players in each cluster), centroids.csv (table with each centroid as rows and each columns for the centroids statistics), output.csv (table with each player as rows and columns for players statistics, metadata, 2-D projection for plotting, and cluster assignment).

Dash App:
- app_combined.py: App powered by Dash which displays and allows filtering for data in centroids.csv and output.csv.

INSTALLATION

1. Install Python and the following Python packages: Jupyter Notebooks, pandas, matplotlib, numpy, scipy, seaborn, sklearn, IPython, json, requests, ratelimit, dash, dash_bootstrap_components, plotly, copy, timeit, csv, functools
2. Open the terminal and navigate to the directory with the Net Value package.
3. Run "python app_combined_final.py" in the terminal to locally host the Net Value dashboard.
