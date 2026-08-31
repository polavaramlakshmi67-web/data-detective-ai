import sys
from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__)
        .resolve()
        .parent
    ),
)


from ai_insights import (
    calculate_evidence,
    investigate,
    generate_explanation,
)


def build_report(
    results,
    conclusion,
):

    lines = []

    lines.append(
        "# NovaMart Data Detective Report"
    )

    lines.append("")

    lines.append(
        "## Executive Summary"
    )

    lines.append("")

    strongest = conclusion[
        "strongest_signal"
    ]

    score = conclusion[
        "score"
    ]

    lines.append(
        f"The strongest evidence signal "
        f"is **{strongest}** with an "
        f"evidence score of "
        f"**{score:.1f}/100**."
    )

    lines.append("")

    lines.append(
        "The score represents the strength "
        "of the observed signal. It should "
        "not be interpreted as proof of "
        "causation."
    )

    lines.append("")

    lines.append(
        "## Evidence Ranking"
    )

    lines.append("")

    lines.append(
        "| Signal | Evidence Score |"
    )

    lines.append(
        "|---|---:|"
    )

    for item in conclusion[
        "ranking"
    ]:

        lines.append(
            f"| {item['cause'].title()} | "
            f"{item['score']:.1f} |"
        )

    lines.append("")

    lines.append(
        "## Investigation"
    )

    lines.append("")

    for cause, data in results.items():

        lines.append(
            f"### {cause.title()}"
        )

        lines.append("")

        if cause == "inventory":

            lines.append(
                f"- Average stock before "
                f"problem: "
                f"{data['before_average_stock']:.1f}"
            )

            lines.append(
                f"- Average stock during "
                f"problem: "
                f"{data['problem_average_stock']:.1f}"
            )

            lines.append(
                f"- Stock change: "
                f"{data['change_percent']:.1f}%"
            )

        elif cause == "support":

            lines.append(
                f"- Average out-of-stock "
                f"tickets before: "
                f"{data['before_average_tickets']:.1f}"
            )

            lines.append(
                f"- Average out-of-stock "
                f"tickets during problem: "
                f"{data['problem_average_tickets']:.1f}"
            )

            lines.append(
                f"- Ticket change: "
                f"{data['change_percent']:.1f}%"
            )

        elif cause == "marketing":

            lines.append(
                f"- Average campaign "
                f"clicks before: "
                f"{data['before_average_clicks']:.1f}"
            )

            lines.append(
                f"- Average campaign "
                f"clicks during problem: "
                f"{data['problem_average_clicks']:.1f}"
            )

            lines.append(
                f"- Click change: "
                f"{data['change_percent']:.1f}%"
            )

        lines.append("")

    lines.append(
        "## Detective Conclusion"
    )

    lines.append("")

    lines.append(
        conclusion["explanation"]
    )

    lines.append("")

    lines.append(
        "**Recommended next investigation:** "
        "compare product-level inventory, "
        "sales volume, and out-of-stock "
        "complaints to determine whether "
        "inventory constraints consistently "
        "precede revenue declines."
    )

    lines.append("")

    lines.append("---")

    lines.append(
        "Generated automatically by "
        "Data Detective AI."
    )

    return "\n".join(lines)


def save_report(
    report,
    reports_folder,
):

    reports_folder = Path(
        reports_folder
    )

    reports_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        reports_folder
        / "novamart_investigation.md"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    return report_path


if __name__ == "__main__":

    project_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    data_folder = (
        project_root / "data"
    )

    reports_folder = (
        project_root / "reports"
    )

    evidence = calculate_evidence(
        data_folder
    )

    results = investigate(
        evidence
    )

    conclusion = generate_explanation(
        results
    )

    report = build_report(
        results,
        conclusion,
    )

    report_path = save_report(
        report,
        reports_folder,
    )

    print()
    print("=" * 70)
    print(
        "REPORT GENERATED"
    )
    print("=" * 70)

    print()
    print(
        f"Saved to: {report_path}"
    )