from setuptools import setup, find_packages

setup(
    name="bibliometric_web_app",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
        "pandas",
        "requests",
        "matplotlib",
        "anthropic",
    ],
    entry_points={
        "console_scripts": [
            "bibliometric=cli.pipeline_executor_main:main",
        ],
    },
    description="A bibliometric analysis and literature review tool",
    author="User",
    author_email="user@example.com",
)