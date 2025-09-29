import numpy as np
import numpy.typing as npt
import plotly.express as px
import plotly.graph_objects as go


def generate_meanip(frames: npt.NDArray) -> npt.NDArray:
    return np.mean(frames, axis=0)


def plot_frame_shifts(
    frame_shifts: npt.NDArray,
    label: str = "",
    as_html: bool = False,
) -> str | go.Figure:
    fig = go.Figure(
        layout=go.Layout(
            xaxis={"title": {"text": "Frame index"}},
            yaxis={"title": {"text": "Displacement (µm)"}},
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )
    )

    fig.add_trace(go.Scatter(y=frame_shifts, mode="lines", name=label))

    if as_html:
        return fig.to_html(full_html=False)
    return fig


def plot_projection(data: npt.NDArray, as_html: bool = False) -> str | go.Figure:
    """Plots a projection using Plotly.

    Args:
        data (npt.NDArray): The projection data to plot as a NumPy array.
        as_html (bool, optional): If True, returns the plot as an HTML string. If False, returns a Plotly Figure object.

    Returns:
        str | go.Figure: The plot as an HTML string if `as_html` is True, otherwise a Plotly Figure object.
    """
    if as_html:
        return px.imshow(data).to_html(full_html=False)
    return px.imshow(data)
