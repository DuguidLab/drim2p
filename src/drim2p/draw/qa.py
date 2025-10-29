import numpy as np
import numpy.typing as npt
import plotly.express as px
import plotly.graph_objects as go


def plot_rois(mean_projection: npt.NDArray, rois: list[npt.NDArray], as_html: bool = False) -> str | go.Figure:
    """Plots drawn ROIs on the mean projection image.

    Args:
        mean_projection (npt.NDArray): The mean projection image as a NumPy array.
        rois (list[npt.NDArray]): A list of ROIs, each represented as a NumPy array of coordinates.
        as_html (bool, optional): If True, returns the plot as an HTML string. If False, returns a Plotly Figure object.

    Returns:
        str | go.Figure: The plot as an HTML string if `as_html` is True, otherwise a Plotly Figure object.
    """
    fig = px.imshow(mean_projection, color_continuous_scale="gray")
    fig.update_layout(
        height=1000,
    )

    for roi in rois:
        fig.add_trace(go.Scatter(x=np.append(roi[:, 1], roi[0, 1]), y=np.append(roi[:, 0], roi[0, 0])))

    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    if as_html:
        return fig.to_html(full_html=False)
    return fig
