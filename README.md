# resolvata
Related data asset path resolving.

## Abstract
Sometimes during data analysis you need to load related data files which are specified
in relation to the current loaded data. For example, a
[GLTF](https://github.com/KhronosGroup/glTF) 3D mesh might have texture image data in
sibling files.

However, you don't want to have to download the entire data directory to get the
specified data files, or you might not know (or care) how the current data was loaded.

This is where *resolvata* comes in: when you pass a relative path, you can get either
the full path or a file-object ready for stream.

## Features
Features:
* Resolver ABCs for custom file download/upload
* Load filesystem resolver implementations

What *resolvata* doesn't do:
* Everything else

## Installation
```bash
pip install resolvata
```

## Usage
### Example
```python
import resolvata
import boto3


class S3Resolver(resolvata.ResolverABC):
    def __init__(self, bucket, prefix):
        self.bucket = bucket
        self.prefix = prefix
        self.client = boto3.client("s3")

    def get_path(self, name):
        return f"s3://{self.bucket}/{self.prefix}{name}"

    def read_into(self, name, stream):
        self.client.download_fileobj(self.bucket, self.prefix + name, stream)

    def write_from(self, name, stream):
        self.client.upload_fileobj(stream, self.bucket, self.prefix + name)


resolver = S3Resolver("bucket", "prefix")
with resolver.open("file.txt", "r") as f:
    print(f.read())
```
