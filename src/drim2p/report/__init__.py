import click
import logging
import pathlib
import h5py as h5

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape


MOTION_REPORT_TEMPLATE = "motion_correction.html"
SIGNAL_REPORT_TEMPLATE = "signal_extraction.html"
DELTAF_REPORT_TEMPLATE = "deltaf.html"
ROI_REPORT_TEMPLATE = "roi_drawing.html"

env = Environment(loader=PackageLoader("drim2p.report", "templates"), autoescape=select_autoescape())


@click.group()
def report() -> None:
    """Generate preprocessing reports."""


@report.command("motion")
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "-o",
    "--out_dir",
    type=click.Path(dir_okay=True),
    default=".",
    help="Output directory for motion correction report.",
)
def generate_motion_correction_report(
    path: pathlib.Path,
    out_dir: pathlib.Path,
) -> pathlib.Path:
    """Generate report for motion correction preprocessing step.

    Args:
        path (pathlib.Path): Path to motion corrected HDF5 file.
        out_dir (pathlib.Path): Directory where the report will be saved, defaults to current directory.

    Returns:
        pathlib.Path: Path to generated report.
    """
    h5file = h5.File(path)
    session_id = str(path).split("/")[-1].replace(".h5", "")

    template = env.get_template(MOTION_REPORT_TEMPLATE)

    template_identifiers = {
        "session_id": session_id,
        "animal_id": ...,
        "session_date": ...,
        "experiment_id": ...,
        "duration": ...,
        "frame_num": ...,
        "filesize": ...,
        "strategy": ...,
        "max_displacement": ...,
        "processing_time": ...,
        "fig_x_axis_shifts": ...,
        "fig_y_axis_shifts": ...,
        "fig_projection_pre": ...,
        "fig_projection_post": ...,
    }

    out_path = out_dir / pathlib.Path(session_id + "_motion-correction-report.html")
    out_path.write_text(template.render(template_identifiers), encoding="utf-8")

    return out_path


@report.command("roi")
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "-o",
    "--out_dir",
    type=click.Path(dir_okay=True),
    default=".",
    help="Output directory for roi drawing report.",
)
def generate_roi_drawing_report(
    path: pathlib.Path,
    out_dir: pathlib.Path,
) -> pathlib.Path:
    h5file = h5.File(path)
    session_id = str(path).split("/")[-1]

    template = env.get_template(MOTION_REPORT_TEMPLATE)

    template_identifiers = {"session_id": session_id}

    out_path = out_dir / pathlib.Path(session_id + "_roi-drawing-report.html")
    out_path.write_text(template.render(template_identifiers), encoding="utf-8")

    return out_path


@report.command("signal")
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "-o",
    "--out_dir",
    type=click.Path(dir_okay=True),
    default=".",
    help="Output directory for signal extraction report.",
)
def generate_signal_extraction_report(
    path: pathlib.Path,
    out_dir: pathlib.Path,
) -> pathlib.Path:
    h5file = h5.File(path)
    session_id = str(path).split("/")[-1]

    template = env.get_template(MOTION_REPORT_TEMPLATE)

    template_identifiers = {"session_id": session_id}

    out_path = out_dir / pathlib.Path(session_id + "_signal-processing-report.html")
    out_path.write_text(template.render(template_identifiers), encoding="utf-8")

    return out_path


@report.command("deltaf")
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "-o",
    "--out_dir",
    type=click.Path(dir_okay=True),
    default=".",
    help="Output directory for deltaf report.",
)
def generate_deltaf_report(
    path: pathlib.Path,
    out_dir: pathlib.Path,
) -> pathlib.Path:
    h5file = h5.File(path)
    session_id = str(path).split("/")[-1]

    template = env.get_template(MOTION_REPORT_TEMPLATE)

    template_identifiers = {"session_id": session_id}

    out_path = out_dir / pathlib.Path(session_id + "_deltaf-report.html")
    out_path.write_text(template.render(template_identifiers), encoding="utf-8")

    return out_path
