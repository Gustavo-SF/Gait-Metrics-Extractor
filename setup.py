import setuptools

setuptools.setup(
    name="GaitMetricsExtractor", # Replace with your own username
    version="0.0.1",
    author="Gustavo Fonseca",
    author_email="gsfonseca32@gmail.com",
    description="Package dedicated to accelerometer gait metrics extraction.",
    url="https://github.com/gustavo-sf/gaitmetricsextractor",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'numpy',
        'pywavelets',
        'scipy',
        'peakutils',
    ],
    python_requires='>=3.6',
)