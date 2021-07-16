import setuptools


setuptools.setup(
    name="fastbot",
    version="0.2.0",
    author="TrungDoan",
    author_email="trungdoan1309@gmail.com",
    description="botengine module",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'sklearn',
        'scipy',
        'marshmallow',
        'pint',
        'pyyaml',
        'dnspython',
        'pymongo',
        'pyvi',
        'spacy'
    ],
    entry_points={
        'console_scripts': [
            'fastbot = fastbot.cli.__init__:main'
        ]
    }
)
