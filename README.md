# Intel RAPL power monitoring
There are four different files:

* rapl_power_monitoring.sh: Continuously reads energy measurements, converts them to power, and both displays and saves the data as a CSV file.
* rapl_power.sh: Reads energy measurements once, converts them to power, and prints the result.
* rapl_live_plot_web.py: Provides real-time plotting of the CSV data on a web interface.
* rapl_live_plot.py: Offers real-time plotting of the CSV data locally.
