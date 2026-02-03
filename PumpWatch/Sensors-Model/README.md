# Predictive Maintenance Analysis

## Overview
This project focuses on predictive maintenance using sensor data to monitor and predict potential failures in industrial equipment. The analysis involves data preprocessing, exploratory data analysis, and statistical modeling to identify patterns and anomalies in sensor readings.

## Project Structure
The project is organized in a Jupyter Notebook (`Predictive_maintenance.ipynb`) and utilizes a dataset (`sensor.csv`) containing timestamped sensor readings.

### Key Files:
- `Predictive_maintenance.ipynb`: Jupyter Notebook containing the data analysis and modeling code.
- `sensor.csv`: Dataset containing sensor readings and timestamps.

## Dependencies
The project relies on the following Python libraries:
- `pandas`: For data manipulation and analysis.
- `numpy`: For numerical computations.
- `os`: For file and directory operations.

## Data Preprocessing
1. **Data Loading**: The dataset is loaded using `pandas.read_csv`.
2. **Timestamp Handling**: The `timestamp` column is converted to datetime format, and a new `day` column is created for analysis.
3. **Data Cleaning**: Unnecessary columns (`Unnamed: 0`, `timestamp`, `sensor_00`, `sensor_15`, `sensor_50`, `sensor_51`) are dropped to streamline the dataset.

## Exploratory Data Analysis (EDA)
- **Descriptive Statistics**: The `describe()` method is used to generate summary statistics for the dataset, providing insights into the distribution and central tendencies of sensor readings.
- **Visualizations**: The notebook includes visualizations (not shown in the provided code) to explore trends and correlations between sensor readings.

## Key Findings
- The dataset contains 220,320 entries with sensor readings from multiple sensors (`sensor_01` to `sensor_51`).
- Some sensors (e.g., `sensor_15`) have missing or null values, which may require imputation or further investigation.
- The statistical summary reveals variations in sensor readings, which can be used to identify outliers or abnormal patterns.

## Usage
1. **Clone the Repository**: 
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```
2. **Install Dependencies**:
   ```bash
   pip install pandas numpy jupyter
   ```
3. **Run the Notebook**:
   ```bash
   jupyter notebook Predictive_maintenance.ipynb
   ```

```

This README provides a clear overview of the project, its structure, dependencies, and key findings. Adjust the content as needed to match additional details or specific goals of your project.
