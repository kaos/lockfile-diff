
files(
    sources=["**/*.lock", "**/*.test.yaml"]
)

python_requirement(
    resolve="test-pex",
    name="cowsay",
    requirements=["cowsay"],
)

jvm_artifact(
    resolve="test-jvm",
    name="hamcrest",
    group="org.hamcrest",
    artifact="hamcrest-core",
    version="1.3",
)
