import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import pandas as pd
import threading
import time
from pathlib import Path

%gui tk

class RealTimePlotApp:
    """Real-time data plotting using Matplotlib and Tkinter."""
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Plot")
        
        # Setup Matplotlib figure
        self.fig, self.axes = plt.subplots(2, 1, figsize=(5, 4), dpi=100)
        self.ax1, self.ax2 = self.axes[0], self.axes[1]
        
        for ax in self.axes:
            ax.set_title("Live Data")
            ax.set_xlabel("Frequency")
            
        self.ax1.set_ylabel("Magn")
        self.ax2.set_ylabel("Phase")
        
        self.line1, = self.ax1.plot([], [], lw=2)
        self.line2, = self.ax2.plot([], [], lw=2)

        # Embed Matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Initialize data
        self.x_data = []
        self.y1_data = []
        self.y2_data = []

        # tight layout
        self.fig.tight_layout()
        
        # Start animation
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100)

        # Label to display frame render time
        self.frame_time_label = tk.Label(self.root, text="Frame Render Time: N/A", font=("Arial", 12))
        self.frame_time_label.pack()

        # Track last frame render time
        self.last_frame_time = None
        
    def update_plot(self, frame):
        """Update plot with new data."""
        start_time = time.time()  # Start timer for frame rendering
        
        # if len(self.x_data) >= 50:
        #     self.x_data.pop(0)
        #     self.y1_data.pop(0)
        #     self.y2_data.pop(0)
        
        # Fetch new data from a shared data source
        if shared_data:
            freq, magn, phase = shared_data.pop(0)
            self.x_data.append(freq)
            self.y1_data.append(magn)
            self.y2_data.append(phase)

        # Update line data
        self.line1.set_data(self.x_data, self.y1_data)
        self.ax1.set_ylim(min(self.y1_data) - 1, max(self.y1_data) + 1)
        
        self.line2.set_data(self.x_data, self.y2_data)
        self.ax2.set_ylim(min(self.y2_data) - 1, max(self.y2_data) + 1)
        
        for ax in self.axes:
            ax.set_xlim([self.x_data[0], self.x_data[-1]])
        
        # Calculate frame render time
        end_time = time.time()
        frame_render_time = (end_time - start_time) * 1000  # Convert to milliseconds
        self.frame_time_label.config(text=f"Frame Render Time: {frame_render_time:.2f} ms")

        return self.line1, self.line2

# Shared data structure for injecting data
shared_data = []

def read_csv_stream(csv_file, delay=0.000001):
    """Simulate streaming data row-by-row from a CSV file."""
    df = pd.read_csv(csv_file, index_col=0)
    for _, row in df.iterrows():
        shared_data.append((row['Frequency'], row['S21 magn_dB'], row['S21 phase_rad']))
        time.sleep(delay)  # Simulate streaming delay

# Main Tkinter GUI thread
if __name__ == "__main__":
    # Path to your CSV file
    data_dir = Path("/Users/jlr7/Documents") / "fastqi_resonatordata" / "Res0_5863MHz"
    all_csvs = list(data_dir.glob("*.csv"))
    
    csv_file = all_csvs[0]

    root = tk.Tk()
    app = RealTimePlotApp(root)

    # Start the data streaming thread
    data_thread = threading.Thread(target=read_csv_stream, args=(csv_file,), daemon=True)
    data_thread.start()

    # Run the Tkinter event loop
    root.mainloop()
