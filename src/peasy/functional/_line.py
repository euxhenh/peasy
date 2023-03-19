import matplotlib.pyplot as plt


def line_plot(
    x,
    y,
    ax: plt.Axes,
    **axis_params,
):
    ax.plot(x, y)
