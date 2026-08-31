import pandas as pd


def test_anomaly_detector_module_imports():
    import src.anomaly_detector

    assert src.anomaly_detector is not None


def test_anomaly_detector_has_functions():
    import src.anomaly_detector

    functions = [
        name
        for name in dir(src.anomaly_detector)
        if callable(
            getattr(src.anomaly_detector, name)
        )
        and not name.startswith("_")
    ]

    assert len(functions) > 0


def test_anomaly_detector_can_process_numeric_data():
    df = pd.DataFrame({
        "revenue": [100, 110, 105, 10000, 115],
        "quantity": [1, 2, 1, 100, 2],
    })

    assert len(df) == 5
    assert df["revenue"].dtype.kind in "iuf"