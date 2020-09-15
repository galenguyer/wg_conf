import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wg_conf",
    version="0.9.0",
    author="Galen Guyer",
    author_email="galen@galenguyer.com",
    description="Manage Wireguard configuration files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/galenguyer/wg_conf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.6',
)