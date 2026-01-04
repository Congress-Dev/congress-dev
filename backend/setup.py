from setuptools import setup, find_packages

setup(
    name='congress',
    version='1.0.0',
    author='Congress.Dev',
    author_email='mustyoshi@gmail.com',
    description='Congress.Dev Packages',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Congress-Dev/congress-dev',
    packages=find_packages(exclude=['tests'], include=["congress_parser", "congress_db", "congress_api", "congress_fastapi"]),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[],
)