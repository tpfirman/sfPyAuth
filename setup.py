from setuptools import setup, find_packages

requirements = []
with open("requirements.txt", encoding="utf-16") as f:
    for line in f:
        requirements.append(line.strip())

if __name__ == "__main__":
    setup(
        name="sfPyAuth",
        version="0.1.0",
        packages=find_packages(where="sfPyAuth"),
        package_dir={"": "src"},
        install_requires=requirements,
        author="Tim Firman",
        description="A pyhton library for authenticating with Salesforce using OAuth 2.0",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        url="https://github.com/tpfirman/sfPyAuth",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: GNU GENERAL PUBLIC LICENSE",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries",
        ],
        python_requires=">=3.12.4",
        include_package_data=True,
    )

print("Setup complete.")
