
## Version information
- aws-cdk@2.0.0-rc.15
- python-3.8

## Services directory
In this directory, it has service-level example constructs(stacks).  
It has no dependency between themselve.  
if it has dependency, must be written to description.

## Solutions directory
In this directory, it as solution-level example constructs(stacks).

## The way of using this example
You must be prepared aws-cdk(CLI) version 2 and cdk bootstrap
```
sudo npm install -g aws-cdk@2.0.0-rc.15
cdk bootstrap
```

First, you can cloning this example code, and copy basis solution.
```
mkdir new-project

git clone https://github.com/wsscc2021/aws-cdk-example.git
cp -r aws-cdk-example/solutions/basis/* new-project
```

Second, you can written constructs(stacks) that reference to example in /service directory.
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cdk list
cdk deploy <stack-name>
```
