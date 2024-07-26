from setuptools import setup


extras = {}
extras["dev"] = ["black ~= 23.0", "ruff>=0.2"]

setup(
    name="txt-from-pdf",
    version="1.3.0",
    description="Extract clean text from PDFs.",
    license_files=["LICENSE"],
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="pdf text extraction",
    license="Apache",
    author="Ali Safaya",
    author_email="alisafaya@gmail.com",
    url="https://github.com/alisafaya/txt-from-pdf",
    entry_points={
        "console_scripts": [
            "txt-from-pdf = txtfrompdf.__main__:cli_main",
        ]
    },
    python_requires=">=3.7.0",
    install_requires=[
        "unicodedata2 ~= 15.1.0",
        "PyMuPDF ~= 1.24.9"
    ],
    extras_require=extras,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
)

# Release checklist
# 1. Change the version in __init__.py and setup.py.
# 2. Commit these changes with the message: "Release: VERSION"
# 3. Add a tag in git to mark the release: "git tag VERSION -m 'Adds tag VERSION for pypi' "
#    Push the tag to git: git push --tags origin main
# 4. Run the following commands in the top-level directory:
#      python setup.py bdist_wheel
#      python setup.py sdist
# 5. Upload the package to the pypi test server first:
#      twine upload dist/* -r pypitest
#      twine upload dist/* -r pypitest --repository-url=https://test.pypi.org/legacy/
# 6. Check that you can install it in a virtualenv by running:
#      pip install -i https://testpypi.python.org/pypi txt-from-pdf
# 7. Upload the final version to actual pypi:
#      twine upload dist/* -r pypi
# 8. Add release notes to the tag in github once everything is looking hunky-dory.
# 9. Update the version in __init__.py, setup.py to the new version "-dev" and push to master
