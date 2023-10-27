import os
from nextcord import User
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from typing import List, Optional
from src.extra.scripts.imgur import upload_image_to_imgur


def custom_formatter(x, pos):
    if x >= 1_000_000_000:
        return '{:0.2f}b'.format(x*1e-9)
    if x >= 1_000_000:
        return '{:0.1f}m'.format(x*1e-6)
    if x >= 1_000:
        return '{:0.0f}k'.format(x*1e-3)
    return str(x)


def plot_data(
        x: List[float], 
        y: List[float],
        user: User,
        plot_type: str = 'line',
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: Optional[str] = 'g',
        marker: Optional[str] = 'o',
        linestyle: Optional[str] = '-',
        grid: bool = True,
        grid_color: Optional[str] = '#4A4E5A',
        background_color: Optional[str] = '#2B2D31',
        label_color: Optional[str] = 'white',
        title_size: int = 18,
        label_size: int = 16,
        tick_label_size: int = 14
    ) -> None:
    
    
    fig: Figure = None
    ax: Axes = None
    fig, ax = plt.subplots(figsize=(10,6))

    if plot_type == 'line':
        ax.plot(x, y, color=color, marker=marker, linestyle=linestyle)
    elif plot_type == 'scatter':
        ax.scatter(x, y, color=color, marker=marker)
    elif plot_type == 'bar':
        ax.bar(x, y, color=color)

    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    
    ax.yaxis.set_major_formatter(FuncFormatter(custom_formatter))
    ax.tick_params(axis='both', colors=label_color, labelsize=tick_label_size)
    ax.xaxis.label.set_color(label_color)
    ax.xaxis.label.set_size(label_size)
    ax.yaxis.label.set_color(label_color)
    ax.yaxis.label.set_size(label_size)
    ax.title.set_color(label_color)
    ax.title.set_size(title_size)
    
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if grid:
        ax.grid(True, color=grid_color)

    path = f"src/save/temp/sc/{user.id}_temp.png"
    plt.savefig(path, dpi=300)
    img_url = upload_image_to_imgur(path)
    print(img_url)
    plt.close(fig)
    os.remove(path)

    return img_url
