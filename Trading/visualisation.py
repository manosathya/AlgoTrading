import matplotlib.pyplot as plt

async def update_plot(ticker, rsi_value):
    """
    Updates the real-time plot for RSI values.
    """
    rsi_values[ticker].append(rsi_value)

    # Initialize the plot for real-time RSI updates (if not already initialized)
    if not hasattr(update_plot, "fig"):
        update_plot.fig, update_plot.ax = plt.subplots(figsize=(10, 6))
        update_plot.ax.axhline(y=30, color='r', linestyle='--', label="Oversold (30)")
        update_plot.ax.axhline(y=70, color='g', linestyle='--', label="Overbought (70)")
        update_plot.ax.set_title(f"RSI for {ticker}")
        update_plot.ax.set_xlabel("Time")
        update_plot.ax.set_ylabel("RSI Value")
        update_plot.ax.legend()

    # Update the plot with the latest RSI value
    update_plot.ax.plot(rsi_values[ticker], label=f'{ticker} RSI')
    update_plot.fig.canvas.draw()  # Update the plot in real-time
    update_plot.fig.canvas.flush_events()  # Ensure the plot updates in Jupyter
    plt.pause(0.01)  # Pause for a short moment to allow for real-time updates