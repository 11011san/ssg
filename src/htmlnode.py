from functools import reduce


class HtmlNode:

    def __init__(self, tag:str = None, value:str = None, children: list["HtmlNode"] = None, props:dict[str, str] = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if not self.props:
            return ""
        return reduce(lambda s, item: s + f" {item[0]}=\"{item[1]}\"",self.props.items(),"")

    def __repr__(self):
        return f"HtmlNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.tag == other.tag and self.value == other.value and self.children == other.children and self.props == other.props

class LeafNode(HtmlNode):

    def __init__(self, value:str, tag:str = None, props:dict[str, str] = None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("value cannot be None")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"

class ParentNode(HtmlNode):

    def __init__(self, tag:str, children: list["HtmlNode"], value:str = None, props:dict[str, str] = None):
        super().__init__(tag, value, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("tag cannot be None")
        if self.children is None:
            raise ValueError("children cannot be None")
        return f"<{self.tag}{self.props_to_html()}>{reduce(lambda s, child: s + child.to_html(), self.children, "")}</{self.tag}>"

    def __repr__(self):
        return f"ParentNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"