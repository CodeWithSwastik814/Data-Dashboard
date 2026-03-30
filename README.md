Overview
A desktop data analytics dashboard for exploring the Netflix titles dataset. Built with Python and PyQt5/6, the app provides an interactive GUI with animated visualizations — including bar, pie, line, scatter, heatmap, and histogram charts — all rendered inline using Matplotlib.

The project is split into two modules:
•	netflix_analysis.py
•	Handles all data processing and chart generation. Export functions save PNGs directly — no plt.show() calls.
•	dashboard.py
•	Full PyQt5/6 GUI with sidebar navigation, animated stat cards, and embedded Matplotlib canvases.

File Structure
florest/
├── netflix_analysis.py   # Data processing & chart exports
├── dashboard.py          # PyQt5/6 GUI dashboard
├── netflix_titles.csv    # Dataset (place here)
└── *.png                 # Exported chart images


Requirements
Package	Purpose / Notes
pandas	Data loading and transformation
matplotlib	Chart rendering and animation
seaborn	Heatmap and styled countplot charts
numpy	Numerical operations
PyQt5 or PyQt6	Desktop GUI framework — either version is auto-detected

Install all dependencies with:
pip install pandas matplotlib seaborn numpy PyQt5


Setup & Usage
1.  Clone the repository
git clone https://github.com/your-username/florest-netflix.git
cd florest-netflix

2.  Add the dataset
Download the Netflix Movies and TV Shows dataset from Kaggle and place netflix_titles.csv in the project root.

3.  Launch the dashboard
python dashboard.py

4.  Export charts as PNGs  (optional)
python netflix_analysis.py
This saves six PNG files (1_pie_chart.png through 6_histogram.png) in the project directory.


Charts & Views
View	Description
Overview	Stat cards (titles, movies, shows, countries) + animated top-5 bar chart
Type Split	Animated pie chart — Movies vs TV Shows
Countries	Animated bar chart — top 10 countries by title count
Trend	Animated dual line chart — content added per year 2010–2021
Scatter	Animated scatter — Movies vs TV Shows by year
Ratings	Animated bar chart — content rating distribution
Heatmap	Seaborn heatmap — content volume by year and type


Key Design Decisions
•	Thread safety — No plt.show() in analysis module
•	Background exports — Export functions run in daemon threads via threading.Thread, keeping the GUI responsive
•	Qt thread safety — A pyqtSignal bridges worker threads back to the Qt main thread for safe QMessageBox calls
•	Animation lifecycle — All animations store references in self._anims to prevent garbage collection mid-render
•	Scatter animation — scatter.set_offsets() is used for scatter animation — the correct API for FuncAnimation with scatter plots


Contributing
Pull requests are welcome. For significant changes, please open an issue first to discuss what you would like to change.

•	Fork the repo and create a feature branch: git checkout -b feature/your-feature
•	Commit your changes: git commit -m 'Add your feature'
•	Push to the branch: git push origin feature/your-feature
•	Open a Pull Request


License
This project is licensed under the MIT License. See LICENSE for details.
