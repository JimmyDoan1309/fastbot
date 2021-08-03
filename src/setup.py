import setuptools


setuptools.setup(
    name="fastbot",
    version="1.0.0",
    author="TrungDoan",
    author_email="trungdoan1309@gmail.com",
    description="botengine module",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19',
        'scikit-learn>=0.23',
        'sklearn_crfsuite>=0.3.6',
        'scipy>=1.7.0',
        'marshmallow==3.12.2',
        'pint==0.17',
        'pyyaml==5.4.1',
        'dnspython==2.1.0',
        'pymongo>=3',
        'pyvi>=0.1.1',
        'spacy>=3,<3.2',
        'rapidfuzz>=1.4',
        'python-dateutil',
        'fire',
        'regex',
    ],
    entry_points={
        'console_scripts': [
            'fastbot = fastbot.cli.__init__:main'
        ]
    }
)
