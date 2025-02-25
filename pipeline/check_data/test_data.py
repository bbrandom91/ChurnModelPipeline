import scipy.stats
import pandas as pd


def test_class_names(data):

    # Disregard the reference dataset
    _, data = data

    assert data["Churn"].isin([0.0,1.0]).all()


def test_column_ranges(data):

    # Disregard the reference dataset
    _, data = data

    categorical_ranges = {
        "Subscription Type": ("Basic", "Standard", "Premium"),
        "Gender": ("Male", "Female"),
        "Contract Length": ("Quarterly", "Monthly", "Annual")
        }

    for col_name, values in categorical_ranges.items():
        assert data[col_name].dropna().isin(values).all(), (
            f"Column {col_name} failed the test. Found unexpected values for categorical columns. "
        )


    numerical_ranges = {
        "Age": (0, 200), # make sure age is  not negative or really really really large
        "Tenure": (0, 10_000), # some very high range
        "Usage Frequency": (0, 10_000),
        "Payment Delay": (0, 10_000),
        "Total Spend": (0, 10_000_000),
        "Last Interaction": (0, 10_000),
    }

    for col_name, (minimum, maximum) in numerical_ranges.items():
        assert data[col_name].dropna().between(minimum, maximum).all(), (
            f"Column {col_name} failed the test. Should be between {minimum} and {maximum}, "
            f"instead min={data[col_name].min()} and max={data[col_name].max()}"
        )


def test_kolmogorov_smirnov(data, ks_alpha):

    sample1, sample2 = data

    columns = [
        "Age",
        "Tenure",
        "Usage Frequency",
        "Payment Delay",
        "Total Spend",
        "Last Interaction",
    ]

    # Bonferroni correction for multiple hypothesis testing
    alpha_prime = ks_alpha/len(columns)

    for col in columns:

        ts, p_value = scipy.stats.ks_2samp(sample1[col], sample2[col])

        # a low p-value suggests data drift, and so we may want to take another look at the data
        assert p_value > alpha_prime