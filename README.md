## Services directory
- It has service-level example constructs(stacks) in this directory.  
- It has no dependency between themselve.  
- If it has dependency, must be written to description.

## Solutions directory
- It has solution-level example constructs(stacks) in this directory.

## The way of using this example
You must be prepared aws-cdk(CLI) and cdk bootstrap  
!! aws-cdk(CLI) version must be same aws-cdk-lib version  

`setup.py`
```
setuptools.setup(
    ...
    install_requires=[
        "aws-cdk-lib==2.1.0",
        "constructs>=10.0.0"
    ],
```

```
sudo npm install -g aws-cdk@2.1.0
cdk bootstrap
```

You can cloning this example code and copy basis solution.
```
mkdir new-project

git clone https://github.com/wsscc2021/aws-cdk-example.git
cp -r aws-cdk-example/solutions/basis/* new-project
```

You can written constructs(stacks) that reference to example in services directory.
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cdk list
cdk deploy <stack-name>
```