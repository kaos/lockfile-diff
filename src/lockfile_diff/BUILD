python_sources()

python_distribution(
    name="dist",
    dependencies=[":lockfile_diff"],
    repositories=["@pypi"],
    provides=python_artifact(
        name="lockfile-diff",
        version="0.3.1",
        description="Diff changes in lockfiles.",
        license="MIT",
        project_urls={
            "Documentation": "https://github.com/kaos/lockfile-diff/wiki",
            "Source": "https://github.com/kaos/lockfile-diff",
            "Tracker": "https://github.com/kaos/lockfile-diff/issues",
        },
        long_description_content_type="text/markdown",
        long_description="""
`lockfile-diff`
===============

Print a summary of what have changed in a given lockfile.

""",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python",
            "Topic :: Software Development",
        ],
    ),
    entry_points={
        "console_scripts": {
            "lockfile-diff": ":bin",
        },
    },
)

python_tests(
    name="tests",
)

pex_binary(
    name="bin",
    entry_point="lockfile_diff.__main__:main",
)
