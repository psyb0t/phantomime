from setuptools import setup, find_packages

setup(
    name='phantomime',
    version='v2.3.3-alpha',
    packages=find_packages(),
    url='https://github.com/psyb0t/phantomime',
    license='WTFPL',
    author='Ciprian Mandache',
    author_email='psyb0t@51k.eu',
    description='An embeddable headless browser package for Python that provides a simplified interface for interacting with web pages using Selenium and Selenium Hub.',
    install_requires=[
        "backoff==2.2.1",
        "selenium==4.7.2",
        "setuptools==65.5.1",
        "docker==6.0.1",
    ],
)
