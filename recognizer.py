import time
import hashlib
from pathlib import Path
from typing import Dict, Tuple, Union
import xdg
from PIL import Image

class Recognizer:
    def __init__(self, classes_dir: Path):
        self.hash_to_class: Dict[bytes, Union[str, Tuple[str, int]]] = {}
        for class_dir in classes_dir.iterdir():
            if not class_dir.is_dir(): continue
            c = class_dir.name
            if c == '.git': continue
            if '-' in c:
                s = c.split('-')
                c = (s[0], int(s[1])) # e.g., ('black', 6)
            for image_file in class_dir.iterdir():
                with Image.open(image_file) as image:
                    image = image.convert("RGB")
                    data = list(image.getdata())
                    data = bytes(i for j in data for i in j)
                    hasher = hashlib.sha1()
                    hasher.update(data)
                    hash = hasher.digest()
                    self.hash_to_class[hash] = c

    def __call__(self, image):
        image = image.convert("RGB")
        data = list(image.getdata())
        data = bytes(i for j in data for i in j)
        hasher = hashlib.sha1()
        hasher.update(data)
        hash = hasher.digest()
        try:
            return self.hash_to_class[hash]
        except KeyError:
            mistake_dir = xdg.XDG_RUNTIME_DIR / 'exapunks-solitaire'
            mistake_name = str(time.monotonic_ns())+'.png'
            image.save(str(mistake_dir / mistake_name))
            raise

if __name__ == '__main__':
    print(Recognizer(Path('data/')).hash_to_class)
