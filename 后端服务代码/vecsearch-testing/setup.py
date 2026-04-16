from setuptools import setup, find_packages

setup(
    name="vecsearch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "numpy==1.23.5",
        "torch==2.0.1",
        "huggingface-hub==0.16.4",
        "transformers==4.30.2",
        "sentence-transformers==2.2.2",
        "faiss-cpu==1.7.4",
        "pydantic>=2.4.2",
        "python-dotenv>=1.0.0",
        "pytest==7.4.3",
        "httpx==0.25.2"
    ],
) 