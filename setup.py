from setuptools import setup, find_packages

PROD_PACKAGES = [
    'fastapi[standard]',
    'pydantic',
]

DEV_PACKAGES = [
    'jupyter-notebook',
]

TEST_PACKAGES = ['pytest', 'ruff', 'mypy', 'vulture', 'types-PyYAML']

setup(
    name='Learnle',
    version='0.0.0',
    packages=find_packages(),
    install_requires=PROD_PACKAGES,
    extras_require={
        'dev': PROD_PACKAGES + TEST_PACKAGES,
    },
    entry_points={
        'console_scripts': ['learnle=learnle_site.cli:main'],
    },
)
