# Marvis

This tool was renamed to Marvis. See the new repository: https://github.com/diselab/marvis

# cohydra

[![master](https://api.travis-ci.com/osmhpi/cohydra.svg?branch=master)](https://travis-ci.com/osmhpi/cohydra)

## Contributors

 - Malte Andersch
 - Arne Boockmeyer
 - Felix Gohla
 - Martin Michaelis
 - Benedikt Schenkel
 - Robert Schmid

## Installation

### Installation With Docker

Cohydra can be obtained via docker.
The easiest solution is using the VSCode *Remote - Containers* extension.
After cloning the repository and opening it in the container, your scenarios will by executing them with `python3`.

Otherwise, you can build the [Dockerfile](./Dockerfile) in the project's root directory yourself by running `make`. In the container, cohydra will be added to your
`PYTHONPATH`. But you need to make sure, that you run the container with privileges to access the host network in order to have access to the host's network interfaces. You of course need to modify the volume mount to allow cohydra access to your scenarios.

```sh
docker run -it --rm --cap-add=ALL -v /var/run/docker.sock:/var/run/docker.sock --net host --pid host --userns host --privileged osmhpi/cohydra:latest
```

The main image [`osmhpi/cohydra`](https://hub.docker.com/r/osmhpi/cohydra) is based on the images in the [docker](./docker) directory.
The [`osmhpi/cohydra:base`](./docker/cohydra-base/Dockerfile) image installs all neccessary dependencies for cohydra,
[`osmhpi/cohydra:dev`](./docker/cohydra-dev/Dockerfile) is for development purposes (docker-cli in the container).

### Installation Without Docker

Recommended python version: Python 3.7

In the case you do not want to use the prebuilt docker, a normal ns-3 installation with *NetAnim* Python bindings will work, too.
To easily install these have a look at our [python wheels repository](https://github.com/osmhpi/python-wheels).

You also need the following packages:
```shell script
sudo pip3 install pyroute2 nsenter docker paramiko
sudo pip3 install git+https://github.com/active-expressions/active-expressions-static-python
```

The Python libraries / directory provided by ns-3 and all other packages has to be in your `PYTHONPATH`, though.
To run an example testcase, go to the example folder and run:
```shell script
python3 basic_example.py
```

Cohydra so far has only been tested with **Debian 10 Buster** and **Ubuntu 18.04 Bionic Beaver**.

## Contribution

We are always happy when somebody contributes to cohydra.
Therefore please create a fork and create a pull request to our repository.
Make sure, that [`pylint`](https://www.pylint.org/) does not show any additional errors or warnings.
Also make sure that your code and your pull request is well documented.
The documentation should also contain how to test your feature, if it is more complex.
Afterwards we are going to test your new feature and review the code.
