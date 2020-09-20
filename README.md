# Paragraph Shortener
Shortens the paragraph depending on the given keywords. Levenshtein distance method is used for keyword similarity detection.

## Installation
In order to `clone` the complete content of this folder use the command:

```git
git clone git@github.com:redrussianarmy/paragraph-shortener.git
```

## Usage
```
root  
└── shortener.py  
└── yourmain.py  
└── ...
```

```python
from shortener import ParagraphShortener
shortener = ParagraphShortener()
result = shortener.run(keyword, paragraph)
```

## License
MIT
