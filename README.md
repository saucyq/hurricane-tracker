# Hurricane Visualization Project

## Project Goal

This project aims to visualize the increasing frequency and intensity of hurricanes over time, and correlate this trend with rising global temperatures. By presenting this data in an interactive and accessible format, we aim to raise awareness about the impact of global warming on extreme weather events.

Google docs: <https://docs.google.com/document/d/1tGITPmFbZ6HCB-iw0fYsj_OWZjvRsIe4wqQRAlmJrNI/edit?tab=t.0>

## User Guide

### Installation

To get started, clone the repository locally using the following command:

```bash
git clone https://github.com/saucyq/hurricane-tracker.git
```

Next, you need to create a Python Virtual Environment to install the required libraries:

```bash
python -m venv /path/to/new/virtual/environment
```

A text file is provided in the repository that you need to install in the newly created virtual environment:

```bash
/venv/Script/activate.bat
pip install -r requirements.txt
```

Finally, once the virtual environment is set up, you can execute the Python script `app.py` directly from a terminal:

```bash
python dashboard/app.py
```

Once the code is running, a link will be provided. Simply open it in a web browser.

```bash
http://127.0.0.1:8050/
```

## Visualization Components

1. **Interactive Heatmap:**

   - A heatmap will display hurricane landfall locations.
   - Color intensity will represent hurricane frequency and/or intensity in a given area.
   - A time slider or animation will allow users to observe changes in hurricane patterns over time, with a step of 10 years.

2. **Temperature Graph:**
   - A line graph will illustrate the change in average global temperature over the same time period as the hurricane data.
   - This graph will be positioned to allow for easy comparison with the hurricane heatmap, reinforcing the correlation between rising temperatures and hurricane activity.

## Data Sources

- **Hurricane Data:** Kaggle database (**https://www.kaggle.com/datasets/thedevastator/atlantic-and-eastern-pacific-hurricane-data**)
  - This dataset provides historical records of hurricane tracks, intensity, and landfall locations.
  - **acronym** status
- WV - Tropical Wave
- TD - Tropical Depression
- TS - Tropical Storm
- HU - Hurricane
- EX - Extratropical cyclone
- SD - Subtropical depression (winds <34 kt)
- SS - Subtropical storm (winds >34 kt)
- LO - A low pressure system not fitting any of above descriptions
- DB - non-tropical Disturbance not have a closed circulation
  NW34/SE34 : Wind speeds of each quadrant at 34 knots (> 50 mph).

- **Global Temperature Data:** Kaggle dataset (**https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data**)
  - This dataset provides reliable global temperature, suitable for demonstrating the long-term warming trend.

## Interactivity

- **Time Slider:** Users can manually control the time period displayed on the heatmap using a slider or animation control.
- **Hover Details:** Hovering over specific points on the heatmap will reveal details about individual hurricanes, such as name, date, category, and potentially associated damages.
- **Zoom/Pan:** Users can zoom in and pan across the heatmap to focus on specific regions of the US.
