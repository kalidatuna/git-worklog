from setuptools import find_packages, setup

setup(
    name="git-worklog",
    version="0.1.0",
    description="Turn local Git commits into Markdown or JSON work summaries",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["git-worklog=git_worklog.cli:main"]},
)
