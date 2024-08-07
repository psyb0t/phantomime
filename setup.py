from setuptools import setup, find_packages

setup(
    name='phantomime',
    version='v2.7.0-beta',
    packages=find_packages(),
    url='https://github.com/psyb0t/phantomime',
    license='WTFPL',
    author='Ciprian Mandache',
    author_email='psyb0t@51k.eu',
    description='An embeddable headless browser package for Python that provides a simplified interface for interacting with web pages using Selenium and Selenium Hub.',
    install_requires=[
        "backoff==2.2.1",
        "selenium==4.8.2",
        "setuptools==70.0.0",
        "docker==6.0.1",
    ],
)
