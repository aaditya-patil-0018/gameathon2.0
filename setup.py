from setuptools import setup, find_packages

setup(
    name="cricket_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "streamlit>=1.22.0",
        "plotly>=5.13.0",
        "tabulate>=0.9.0",
        "numpy>=1.23.0",
    ],
    python_requires=">=3.8",
) 