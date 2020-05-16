import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="k8-kat",
  version="0.0.129",
  author="Nectar Cloud Software",
  author_email="xa1 vier@codenectar.com",
  description="Sugar for Kubernetes",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/nectar-cs/k8-kat",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6'
)
