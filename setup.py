from setuptools import setup, find_packages

PROD_PACKAGES = [
    'fastapi[standard]',
    'pydantic',
    'pydantic-settings',
    'click',
    'uvicorn',
]

DEV_PACKAGES = [
    'jupyter-notebook',
    'PyYAML',
]

TEST_PACKAGES = [
    'pytest',
    'pytest-asyncio',
    'ruff',
    'mypy',
    'types-PyYAML',
    'pyhamcrest',
    'faker',
]

setup(
    name='Learnle',
    version='0.0.0',
    packages=find_packages(),
    install_requires=PROD_PACKAGES,
    extras_require={
        'dev': PROD_PACKAGES + TEST_PACKAGES + DEV_PACKAGES,
        'test': PROD_PACKAGES + TEST_PACKAGES,
    },
    entry_points={
        'console_scripts': ['learnle=learnle.cli:main'],
    },
)
