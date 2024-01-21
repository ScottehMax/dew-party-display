import os
import zipfile

def zipdir(path, ziph):
    for root, _dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".png"):
                ziph.write(os.path.join(root, file))


def unzipdir(path, ziph):
    for root, _dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".png"):
                ziph.extract(os.path.join(root, file), path)


def create_assets_zip():
    zipf = zipfile.ZipFile('assets.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('assets/items', zipf)
    zipdir('assets/pokemon', zipf)
    zipf.close()


def unzip_assets_zip():
    zipf = zipfile.ZipFile('assets.zip', 'r')
    zipf.extractall()
    zipf.close()


if __name__ == '__main__':
    # create_assets_zip()
    unzip_assets_zip()
