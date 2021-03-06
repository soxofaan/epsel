import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epsel",
    version="1.0.0",
    author="Stefaan Lippens",
    description="Ensure PySpark Executor Logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soxofaan/epsel",
    py_modules=["epsel"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    extras_require={
        "dev": [
            "pytest",
            "pyspark",
        ]
    },
)
