# Decision-support system for live detection of Leishmania parasites from microscopic images with Deep Learning

Key Features:
- Real-time prediction of leishmania parasites
- Intuitive user interface for easy use

## Installing / Getting started

A quick introduction of the minimal setup you need to get the livestream running.

Download and install miniconda
https://docs.anaconda.com/miniconda/
```shell
conda create--name leishmania python=3.8
```
```shell
conda activate leishmania
```
```shell
conda install pytorch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 pytorch-cuda=12.1 -c pytorch -c nvidia
```
Test if PyTorch has been installed correctly
```shell
python
```
```shell
import torch
```
```shell
torch.cuda.is_available()
```
Output should be True
```shell
pip install cython==3.0.10 matplotlib opencv-python pillow==6.2.2 numpy==1.23.1 pycocotools ultralytics
```
```shell
cd path_to_MicroPredictor_folder
```
```shell
python create_config.py
```
```shell
python livestream.py
```

## Developing

### Built With
- Python 3.8
- PyTorch 2.1.0
- Torchaudio 2.1.0
- Torchvision 0.16.0
- Cuda 12.1
- NumPy 1.23.1
- Cython 3.0.10
- Pillow 6.2.2
- Ultralytics 8.2.76

<!---
### Setting up Dev

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/your/your-project.git
cd your-project/
packagemanager install
```

And state what happens step-by-step. If there is any virtual environment, local server or database feeder needed, explain here.

### Building

If your project needs some additional steps for the developer to build the
project after some code changes, state them here. for example:

```shell
./configure
make
make install
```

Here again you should state what actually happens when the code above gets
executed.

### Deploying / Publishing
give instructions on how to build and release a new version
In case there's some step you have to take that publishes this project to a
server, this is the right time to state it.

```shell
packagemanager deploy your-project -s server.com -u username -p password
```

And again you'd need to tell what the previous code actually does.

## Versioning

We can maybe use [SemVer](http://semver.org/) for versioning. For the versions available, see the [link to tags on this repository](/tags).


## Configuration

Here you should write what are all of the configurations a user can enter when using the project.

## Tests

Describe and show how to run the tests with code examples.
Explain what these tests test and why.

```shell
Give an example
```

## Style guide

Explain your code style and show how to check it.

## Api Reference

If the api is external, link to api documentation. If not describe your api including authentication methods as well as explaining all the endpoints with their required parameters.


## Database

Explaining what database (and version) has been used. Provide download links.
Documents your database design and schemas, relations etc... 

## Licensing

State what the license is and how to find the text version of the license.
-->
