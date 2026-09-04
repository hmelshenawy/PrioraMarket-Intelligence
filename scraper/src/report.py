"""Run-report assembly (FR-061 basic metrics, FR-023 lineage, dataset version).

US1 assembles the basic run report. Extended (FR-063) and optional
operational (FR-064) metrics and stop-position identification are wired
in Polish (T045/T046/T047). The pipeline writes the report via the
StorageAdapter; this module provides builders/summaries and derived-rate
finalization.
"""

from __future__ import annotations

from typing import Any, Optional

from src.common.models import RunReport, RunState


def finalize(report: RunReport) -> RunReport:
    """Compute derived extended/optional metrics (FR-063/064) in place.

    - pages_per_second / listings_per_second from execution duration.
    - total_duration_seconds from start/end wall-clock timestamps.
    - peak_memory / peak_cpu best-effort via stdlib ``resource`` (POSIX);
      None where unavailable (e.g. Windows). No extra dependencies.
    """
    if report.execution_duration_seconds and report.execution_duration_seconds > 0:
        report.pages_per_second = round(
            report.pages_processed / report.execution_duration_seconds, 3
        )
        report.listings_per_second = round(
            report.listings_extracted / report.execution_duration_seconds, 3
        )
    report.total_duration_seconds = report.execution_duration_seconds
    mem, cpu = _best_effort_resource_usage()
    if mem is not None and report.peak_memory is None:
        report.peak_memory = mem
    if cpu is not None and report.peak_cpu is None:
        report.peak_cpu = cpu
    return report


def _best_effort_resource_usage() -> tuple[Optional[int], Optional[float]]:
    try:
        import resource  # POSIX only; absent on Windows

        usage = resource.getrusage(resource.RUSAGE_SELF)
        # ru_maxrss is in KB on Linux, bytes on macOS; report as bytes-ish.
        peak_mem = int(usage.ru_maxrss) * 1024
        peak_cpu = float(getattr(usage, "ru_utime", 0.0) + getattr(usage, "ru_stime", 0.0))
        return peak_mem, round(peak_cpu, 3)
    except Exception:
        return None, None


def stop_position(report: RunReport) -> dict[str, Any]:
    """Stop-position identification for failure recovery (FR-063, T047).

    Returns where execution stopped: last successful page, failing page,
    and the stage at which the failure occurred. Absent values mean no
    failure was recorded for that dimension.
    """
    return {
        "last_successful_page": report.last_successful_page,
        "failing_page": report.failing_page,
        "failing_stage": report.failing_stage,
    }


def summarize(report: RunReport) -> dict[str, Any]:
    """Operator-facing summary of a run report (basic metrics only)."""
    return {
        "run_id": report.run_id,
        "state": report.state.value,
        "marketplace": report.marketplace,
        "condition": report.condition,
        "make": report.make,
        "dataset_version": report.dataset_version,
        "normalization_version": report.normalization_version,
        "pages_processed": report.pages_processed,
        "listings_extracted": report.listings_extracted,
        "listings_skipped": report.listings_skipped,
        "execution_duration_seconds": report.execution_duration_seconds,
        "failures": report.failures,
    }


def extended_summary(report: RunReport) -> dict[str, Any]:
    """Extended + optional operational metrics (FR-063/064)."""
    base = summarize(report)
    base.update(
        {
            "retry_count": report.retry_count,
            "duplicate_count": report.duplicate_count,
            "validation_failures": report.validation_failures,
            "pages_per_second": report.pages_per_second,
            "listings_per_second": report.listings_per_second,
            "fetch_duration_seconds": report.fetch_duration_seconds,
            "processing_duration_seconds": report.processing_duration_seconds,
            "storage_duration_seconds": report.storage_duration_seconds,
            "start_time": report.start_time,
            "end_time": report.end_time,
            "total_duration_seconds": report.total_duration_seconds,
            "peak_memory": report.peak_memory,
            "peak_cpu": report.peak_cpu,
            "stop_position": stop_position(report),
        }
    )
    return base


def format_summary_text(report: RunReport) -> str:
    s = summarize(report)
    lines = [
        f"Run {s['run_id']} — {s['state']}",
        f"  scope: {s['marketplace']} / {s['condition']} / {s['make']}",
        f"  dataset_version: {s['dataset_version']}",
        f"  pages: {s['pages_processed']}",
        f"  listings: {s['listings_extracted']} extracted, " f"{s['listings_skipped']} skipped",
        f"  duration: {s['execution_duration_seconds']}s",
        f"  failures: {s['failures']}",
    ]
    return "\n".join(lines)


def is_success(report: RunReport) -> bool:
    return report.state == RunState.COMPLETED
