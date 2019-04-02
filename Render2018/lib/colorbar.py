import matplotlib.pyplot as plt
import matplotlib as mpl

def export_colorbar(bound_min, bound_max, output_dir):
    """
    Save an image of the Inferno colorbar with numbers on it, given minimum and maximum bounds.
    :param bound_min: Minimum colorbar value
    :param bound_max: Maximum colorbar value
    :param output_dir: Directory to save colorbar image to
    """

    # Make a figure and axes with dimensions as desired.
    fig = plt.figure(figsize=(4, 12))
    ax1 = fig.add_axes([0.05, 0.05, 0.35, 0.9]) # Axes determined experimentally to work for the vertical configuration
    plt.tick_params(axis='both', which='major', labelsize=40, labelcolor="white")

    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = mpl.cm.inferno
    norm = mpl.colors.Normalize(vmin=bound_min, vmax=bound_max)

    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='vertical')
    cb1.set_label('Temperature (K)', fontsize=50, color=(1,1,1))
    plt.savefig(output_dir, transparent=True) 
