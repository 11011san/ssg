from enum import Enum

class TextType(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    LINKS = "links"
    IMAGES = "images"

class TextNode():

    def __init__(self, text:str, text_type:TextType, url:str = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, othere):
        return self.text == othere.text and self.text_type == othere.text_type and self.url == othere.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
