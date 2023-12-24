from setuptools import setup, find_packages

setup(
    name='billparser',
    version='0.8.7',
    author='Bradley',
    author_email='mustyoshi@gmail.com',
    description='Congress.dev bill parser',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/billparser',
    packages=find_packages(exclude=['tests'], include=["billparser"]),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        # list of your library dependencies
    ],
)