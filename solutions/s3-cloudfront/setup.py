import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="services",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),

    install_requires=[
        "aws-cdk.core==1.115.0",
        "aws-cdk.aws_kms==1.115.0",
        "aws-cdk.aws_iam==1.115.0",
        "aws-cdk.aws_s3==1.115.0",
        "aws-cdk.aws_cloudfront==1.115.0",
        "aws-cdk.aws_cloudfront_origins==1.115.0",
        "aws-cdk.aws_certificatemanager==1.115.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
