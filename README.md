# Aircraft Data Dashboard

An interactive Python dashboard for analyzing Austrian aircraft registry data from Excel files.

## Features

- **Multi-Sheet Support**: Select and analyze data from any sheet in the Excel file
- **Flexible Grouping**: Group data by:
  - Hersteller (Manufacturer)
  - Herstellerbezeichnung (Manufacturer Designation/Model)
  - Both combined
- **Interactive Visualizations**:
  - Bar charts showing top N aircraft counts by selected grouping
  - Density plots with histogram and KDE for maximum takeoff mass distribution
  - Adjustable "Top N" slider (5-30 results)
- **Data Summary**: Quick statistics including total aircraft, unique manufacturers, average and max mass
- **Data Preview**: Sample data table showing first 10 rows

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install pandas openpyxl plotly dash dash-bootstrap-components scipy
```

Or install all at once:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

```bash
python3 dashboard.py
```

The dashboard will start on `http://127.0.0.1:8050/`

Open your web browser and navigate to this URL to access the interactive dashboard.

### Using the Dashboard

1. **Select Sheet**: Choose which aircraft category sheet to analyze from the dropdown
2. **Group By**: Select grouping method:
   - Hersteller (Manufacturer)
   - Herstellerbezeichnung (Model)
   - Both (combined)
3. **Top N Results**: Adjust the slider to show between 5-30 results in the bar chart
4. **View Visualizations**:
   - Left panel: Bar chart of aircraft counts
   - Right panel: Mass distribution density plot
5. **Review Statistics**: Check the summary cards for key metrics
6. **Browse Data**: Scroll through the sample data table at the bottom

## Data Structure

The dashboard expects an Excel file with:
- Multiple sheets for different aircraft categories
- Columns including:
  - `Hersteller` (Manufacturer)
  - `Herstellerbezeichnung` (Manufacturer Designation)
  - `höchstzulässige Abflugmasse (kg)` (Maximum Takeoff Mass in kg)

Default data file location: `data/Stand_2025_10_DE.xlsx`

## Technology Stack

- **Python**: Core programming language
- **Dash**: Web application framework for interactive dashboards
- **Plotly**: Interactive visualization library
- **Pandas**: Data manipulation and analysis
- **Scipy**: Statistical functions (KDE for density plots)
- **Bootstrap**: UI styling via dash-bootstrap-components

## Customization

To use a different Excel file, modify the `EXCEL_FILE` variable in `dashboard.py`:

```python
EXCEL_FILE = 'path/to/your/file.xlsx'
```

To change the port or host:

```python
app.run(debug=True, host='127.0.0.1', port=8050)
```

## Stopping the Dashboard

Press `Ctrl+C` in the terminal where the dashboard is running.

## Troubleshooting

**Issue**: Port 8050 already in use
- **Solution**: Kill the existing process or change the port in the code

**Issue**: Excel file not found
- **Solution**: Verify the file path in `EXCEL_FILE` variable

**Issue**: Missing columns error
- **Solution**: Ensure your Excel file has the expected column structure
