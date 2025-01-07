from enum import Enum
from typing import Any
import re
from htmlnode import LeafNode, ParentNode

class TextType(Enum):
    NORMAL = "normal"
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

class TextNode:

    def __init__(self, text:str, text_type:TextType, url:str = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: Any):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a", props={"href": text_node.url}, value=text_node.text)
        case TextType.IMAGE:
            return ParentNode(tag="img", props={"src": text_node.url, "alt": text_node.text}, children=[])
        case _:
            raise ValueError("Invalid text type")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        types = (node.text_type,text_type)
        i = 0
        if delimiter in node.text:
            if node.text.count(delimiter) % 2 != 0:
                raise ValueError("Invalid Markdown syntax")
            for text in node.text.split(delimiter):
                if text != "":
                    new_nodes.append(TextNode(text, types[i]))
                i = (1 + i)%2
        else:
            new_nodes.append(node)
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        find = extract_markdown_images(old_node.text)
        if find:
            text = old_node.text
            for image in find:
                text = text.split(f"![{image[0]}]({image[1]})", 1)
                if text[0] != "":
                    new_nodes.append(TextNode(text[0], TextType.TEXT))
                new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
                text = text[1]
            if text != "":
                new_nodes.append(TextNode(text, TextType.TEXT))
        else:
            new_nodes.append(old_node)
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        find = extract_markdown_links(old_node.text)
        if find:
            text = old_node.text
            for link in find:
                text = text.split(f"[{link[0]}]({link[1]})", 1)
                if text[0] != "":
                    new_nodes.append(TextNode(text[0], TextType.TEXT))
                new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
                text = text[1]
            if text != "":
                new_nodes.append(TextNode(text, TextType.TEXT))
        else:
            new_nodes.append(old_node)
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown):
    return list(filter(lambda x: x != "",map(lambda x: x.strip(),markdown.split("\n\n"))))

def block_to_block_type(block):
    if re.match(r"^#{1,6} ",block):
        return "heading"
    if block[:3] == "```" and block[-3:] == "```":
        return "code"
    if all(re.match(r"^> ", line) for line in block.splitlines()):
        return "quote"
    if all(re.match(r"^[-*] ", line) for line in block.splitlines()):
        return "unordered_list"
    if do_lines_increment_from_one(block):
        return "ordered_list"
    return "paragraph"

def do_lines_increment_from_one(block):
    lines = block.splitlines()
    numbers = []  # To store the leading numbers

    for line in lines:
        match = re.match(r"^(\d+)\. ", line)
        if match:
            numbers.append(int(match.group(1)))
        else:
            return False  # Line doesn't match the pattern

    # Check if the numbers form a sequence starting from 1
    return numbers == list(range(1, len(numbers) + 1))

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        match block_to_block_type(block):
            case "heading":
                count = block.count('#',0,7)
                nodes.append(text_to_html_nodes(block[count+1:],f"h{count}"))
            case "code":
                nodes.append(ParentNode(tag="pre", children=[text_to_html_nodes(block[4:-3],"code")]))
            case "quote":
                nodes.append(text_to_html_nodes(re.sub(r"^> ","",block,flags=re.M),"blockquote"))
            case "unordered_list":
                nodes.append(ParentNode(tag="ul",children=list(map(lambda x: text_to_html_nodes(x[2:],"li"),block.splitlines()))))
            case "ordered_list":
                nodes.append(ParentNode(tag="ol",children=list(map(lambda x: text_to_html_nodes(re.sub(r"^\d+\. ","",x),"li"),block.splitlines()))))
            case "paragraph":
                nodes.append(text_to_html_nodes(block,"p"))
            case _:
                raise ValueError("Invalid block type")

    return ParentNode(tag="div",children=nodes)


def text_to_html_nodes(block, tag):
    return ParentNode(tag, list(map(text_node_to_html_node, text_to_textnodes(block))))

def extract_title(markdown):
    match = re.search(r"^# (.*)",markdown,re.M)
    if match:
        return match.group(1).strip()
    raise ValueError("No title found")