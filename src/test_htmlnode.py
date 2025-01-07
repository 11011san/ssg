import unittest

from src.htmlnode import HtmlNode, LeafNode, ParentNode
from textnode import TextNode, TextType


class TestHtmlNode(unittest.TestCase):
    def test_props_to_html_none(self):
        node = HtmlNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_zero(self):
        node = HtmlNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_one(self):
        node = HtmlNode(props={"class": "bold"})
        self.assertEqual(node.props_to_html(), " class=\"bold\"")

    def test_props_to_html_two(self):
        node = HtmlNode(props={"class": "bold", "id": "test"})
        self.assertEqual(node.props_to_html(), " class=\"bold\" id=\"test\"")

    def test_str(self):
        node = HtmlNode(props={"class": "bold"})
        self.assertEqual(str(node), "HtmlNode(tag=None, value=None, children=None, props={'class': 'bold'})")



class TestLeafNode(unittest.TestCase):
    def test_to_html_value_none(self):
        node = LeafNode(None)
        self.assertRaises(ValueError,lambda:node.to_html())

    def test_to_html_only_value(self):
        node = LeafNode("test")
        self.assertEqual(node.to_html(), "test")

    def test_to_html_with_tag(self):
        node = LeafNode("test",tag="p")
        self.assertEqual(node.to_html(), "<p>test</p>")

    def test_to_html_with_tag_and_props(self):
        node = LeafNode("test",tag="p",props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\">test</p>")

class TestParentNode(unittest.TestCase):
    def test_to_html_tag_child_none(self):
        node = ParentNode(None,None)
        self.assertRaises(ValueError,lambda:node.to_html())
    def test_to_html_tag_none(self):
        node = ParentNode(None,[])
        self.assertRaises(ValueError,lambda:node.to_html())
    def test_to_html_child_none(self):
        node = ParentNode("p",None)
        self.assertRaises(ValueError,lambda:node.to_html())
    def test_to_html_min(self):
        node = ParentNode("p",[])
        self.assertEqual(node.to_html(), "<p></p>")
    def test_to_html_tag_prop(self):
        node = ParentNode("p",[], props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\"></p>")
    def test_to_html_tag_prop_one_leaf(self):
        node = ParentNode("p",[LeafNode("test")], props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\">test</p>")
    def test_to_html_tag_prop_two_leaf(self):
        node = ParentNode("p",[LeafNode("test","b"),LeafNode("tset","c")], props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\"><b>test</b><c>tset</c></p>")
    def test_to_html_tag_prop_one_parent(self):
        node = ParentNode("p",[ParentNode("d",[])], props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\"><d></d></p>")
    def test_to_html_tag_prop_one_parent_one_leaf(self):
        node = ParentNode("p",[ParentNode("d",[LeafNode("test")])], props={"class": "bold"})
        self.assertEqual(node.to_html(), "<p class=\"bold\"><d>test</d></p>")

