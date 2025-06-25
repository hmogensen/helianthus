import h5py
import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

sunrise_threshold = {'avg_brightness': 30, 
                     'bright_ratio': 0.02, 
                     'hsv_brightness': 20, 
                     'mean_intensity': 20, 
                     'median_intensity': 5, 
                     'sky_brightness': 40}

def load_and_plot_sunlight_data(fpath):
    with h5py.File(fpath, 'r') as f:
        metrics = [key for key in f.keys() if key != 'timestamps']
        print(metrics)
       
        titles = [metric.replace('_', ' ').title() for metric in metrics]       
        timestamps = [datetime.fromtimestamp(ts) for ts in f['timestamps'][:]]
       
        sns.set_style("whitegrid")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12), sharex=True)
        fig.suptitle(f'Sunlight Analysis - {f.attrs["template_name"]}', fontsize=16)
       
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            row, col = divmod(i, 3)
            metric_data = f[metric][:]
            axes[row, col].plot(timestamps, metric_data)
            axes[row, col].set_title(title)
            axes[row, col].tick_params(axis='x', rotation=45)
       
        plt.tight_layout()

        plot_daylight_analysis(timestamps, [f[metric][:] for metric in metrics], metrics, sunrise_threshold)

        plt.show()
            
        # numeric_data = np.column_stack([f[metric][:] for metric in metrics])
        # correlation_matrix = np.corrcoef(numeric_data.T)
        # sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
        #             xticklabels=titles, yticklabels=titles)

def _find_sunrise_sunset(timestamps, intensity_data, threshold):
    sunrises = []
    sunsets = []
    
    above_threshold = intensity_data > threshold
    crossings = np.diff(above_threshold.astype(int))
    
    sunrise_indices = np.where(crossings == 1)[0] + 1
    sunset_indices = np.where(crossings == -1)[0] + 1
    
    sunrises = [timestamps[i] for i in sunrise_indices if i < len(timestamps)]
    sunsets = [timestamps[i] for i in sunset_indices if i < len(timestamps)]
    
    return sunrises, sunsets

def plot_daylight_analysis(timestamps, metrics_data, metrics_names, thresholds):

    for metric_name, metric_data in zip(metrics_names, metrics_data):            
        threshold = thresholds.get(metric_name, 10)  # Default to 10 if metric not in dict
        sunrises, sunsets = _find_sunrise_sunset(timestamps, metric_data, threshold)
        
        daily_data = []
        for sunrise in sunrises:
            sunrise_date = sunrise.date()
            matching_sunset = None
            for sunset in sunsets:
                if sunset.date() == sunrise_date or (sunset.date() - sunrise_date).days == 1:
                    if sunset > sunrise:
                        matching_sunset = sunset
                        break
            
            if matching_sunset:
                day_length = (matching_sunset - sunrise).total_seconds() / 3600  # Convert to hours
                daily_data.append({
                    'date': sunrise_date,
                    'sunrise': sunrise,
                    'sunset': matching_sunset,
                    'day_length': day_length
                })
        
        if not daily_data:
            continue

        if len(daily_data) > 1 and daily_data[0]['day_length'] < 8:
            daily_data = daily_data[1:]

        if not daily_data:
            continue
    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'Daylight Analysis - {metric_name.replace("_", " ").title()}', fontsize=14)
        
        dates = [d['date'] for d in daily_data]
        day_lengths = [d['day_length'] for d in daily_data]
        sunrise_times = [d['sunrise'] for d in daily_data]
        sunset_times = [d['sunset'] for d in daily_data]
        
        ax1.plot(dates, day_lengths, 'o-', color='gold', linewidth=2, markersize=4)
        ax1.set_ylabel('Day Length (hours)')
        ax1.set_title('Length of Day')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        sunrise_hours = [sr.hour + sr.minute/60 + sr.second/3600 for sr in sunrise_times]
        sunset_hours = [ss.hour + ss.minute/60 + ss.second/3600 for ss in sunset_times]
        
        ax2.plot(dates, sunrise_hours, 'o-', color='orange', label='Sunrise', linewidth=2, markersize=4)
        ax2.plot(dates, sunset_hours, 'o-', color='darkred', label='Sunset', linewidth=2, markersize=4)
        ax2.set_ylabel('Time of Day (24-hour)')
        ax2.set_xlabel('Date')
        ax2.set_title('Sunrise and Sunset Times')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        ax2.set_ylim(0, 24)
        ax2.set_yticks(range(0, 25, 2))
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
   fpath = sys.argv[1]
   load_and_plot_sunlight_data(fpath)