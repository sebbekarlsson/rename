from setuptools import setup, find_packages


setup(
    name='rename',
    version='1.0.4',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'rename=rename.cli:run'
        ]
    }
    
)
