
## version infomation
aws-cdk@1.100.0

## services directory
services 디렉터리 안에 각 서비스 단위의 example 파일들이 위치해 있습니다.  
해당 example 파일들은 서로 종속성을 가지고 있지 않습니다.


## solutions directory
solutions 디렉터리 안에는 각 서비스를 조합한 하나의 solutions들을 정리해두었습니다.

## 사용법
```
mkdir new-project

git clone https://github.com/wsscc2021/aws-cdk-example.git
cp -r aws-cdk-example/solutions/basis/* new-project
```

/services 디렉터리 내의 example파일들을 참조하여 과제에 맞는 cdk 추가 작성
```
cdk install -r requirements.txt
cdk list
cdk deploy <stack-name>
```