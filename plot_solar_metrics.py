import h5py
import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def load_and_plot_sunlight_data(fpath):
   with h5py.File(fpath, 'r') as f:
       metrics = [key for key in f.keys() if key != 'timestamps']
       
       titles = [metric.replace('_', ' ').title() for metric in metrics]       
       timestamps = [datetime.fromtimestamp(ts) for ts in f['timestamps'][:]]
       
       data = {'timestamp': timestamps}
       for metric in metrics:
           data[metric] = f[metric][:]
       
       df = pd.DataFrame(data)
       
       sns.set_style("whitegrid")
       fig, axes = plt.subplots(2, 3, figsize=(18, 12))
       fig.suptitle(f'Sunlight Analysis - {f.attrs["template_name"]}', fontsize=16)
       
       for i, (metric, title) in enumerate(zip(metrics, titles)):
           row, col = divmod(i, 3)
           sns.lineplot(data=df, x='timestamp', y=metric, ax=axes[row, col])
           axes[row, col].set_title(title)
           axes[row, col].tick_params(axis='x', rotation=45)
       
       plt.tight_layout()
       plt.show()
       
    #    plt.figure(figsize=(10, 8))
    #    correlation_data = df.select_dtypes(include=[np.number])
    #    sns.heatmap(correlation_data.corr(), annot=True, cmap='coolwarm', center=0)
    #    plt.title('Correlation Matrix of Sunlight Metrics')
    #    plt.tight_layout()
    #    plt.show()

if __name__ == "__main__":
   fpath = sys.argv[1]
   load_and_plot_sunlight_data(fpath)