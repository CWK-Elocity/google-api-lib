from setuptools import setup, find_packages

setup(
    name="google-api-lib",
    version="0.1.8",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client>=2.0.0",
        "google-cloud-secret-manager>=2.0.0",
        "requests>=2.0.0",
    ],
    description="Utilities for working with Google services.",
    author="Patryk Skibniewski",
    author_email="patrykski07@gmail.com",
    url="https://github.com/RyKaT07/google-api-lib",
    python_requires=">=3.7"
)
