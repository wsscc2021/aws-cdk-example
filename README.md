
## version infomation
aws-cdk@1.115.0

## services directory
services 디렉터리 안에 각 서비스 단위의 example 파일들을 작성합니다.
각 서비스는 최대한 종속성을 가지고 있지 않도록 작성합니다.
만약, 종속성을 가질 경우 이를 맨 앞의 description에 기재하도록 합니다.


## solutions directory
solutions 디렉터리 안에는 각 서비스를 조합한 하나의 solutions들을 작성합니다.

## 사용법
```
mkdir new-project

git clone https://github.com/wsscc2021/aws-cdk-example.git
cp -r aws-cdk-example/solutions/basis/* new-project
```

/services 디렉터리 내의 example파일들을 참조하여 과제에 맞는 cdk 추가 작성
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cdk list
cdk deploy <stack-name>
```
