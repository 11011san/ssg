import textwrap
import unittest

from src.htmlnode import LeafNode, ParentNode
from src.textnode import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, \
    split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        self.assertEqual(node, node2)

    def test_eq_not_text(self):
        node = TextNode("This is a text", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq_not_type(self):
        node = TextNode("This is a text node", TextType.IMAGE)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq_not_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_str(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(str(node), "TextNode(This is a text node, bold, https://www.google.com)")
        self.assertEqual(str(node2), "TextNode(This is a text node, bold, None)")

    def test_convert_text(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node), LeafNode("This is a text node"))

    def test_convert_bold(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node), LeafNode("This is a text node", "b"))

    def test_convert_italic(self):
        node = TextNode("This is a text node", TextType.ITALIC, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node), LeafNode("This is a text node", "i"))

    def test_convert_code(self):
        node = TextNode("This is a text node", TextType.CODE, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node), LeafNode("This is a text node", "code"))

    def test_convert_link(self):
        node = TextNode("This is a text node", TextType.LINK, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node),
                         LeafNode("This is a text node", "a", props={"href": "https://www.google.com"}))

    def test_convert_image(self):
        node = TextNode("This is a text node", TextType.IMAGE, "https://www.google.com")
        self.assertEqual(text_node_to_html_node(node),
                         ParentNode(tag="img", props={"src": "https://www.google.com", "alt": "This is a text node"},
                                    children=[]))

    def test_split_nothing(self):
        nodes = [TextNode("This is a text node", TextType.TEXT)]
        self.assertListEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), nodes)

    def test_split_one(self):
        nodes = [TextNode("This is **a** text node", TextType.TEXT)]
        self.assertListEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD),
                             [TextNode("This is ", TextType.TEXT), TextNode("a", TextType.BOLD),
                              TextNode(" text node", TextType.TEXT)])

    def test_split_one(self):
        nodes = [TextNode("This is **a** text node", TextType.TEXT)]
        self.assertListEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD),
                             [TextNode("This is ", TextType.TEXT), TextNode("a", TextType.BOLD),
                              TextNode(" text node", TextType.TEXT)])

    def test_split_two(self):
        nodes = [TextNode("This is **a** text **node**", TextType.TEXT)]
        self.assertListEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD),
                             [TextNode("This is ", TextType.TEXT), TextNode("a", TextType.BOLD),
                              TextNode(" text ", TextType.TEXT), TextNode("node", TextType.BOLD)])

    def test_split_non_text(self):
        nodes = [TextNode("This is a text node", TextType.BOLD)]
        self.assertListEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), nodes)

    def test_extract_markdown_images(self):
        self.assertListEqual(extract_markdown_images("[test1](https://www.google1.com)"),
                             [])
        self.assertDictEqual(dict(extract_markdown_images("![test](https://www.google.com)")),
                             dict([("test", "https://www.google.com")]))
        self.assertDictEqual(
            dict(extract_markdown_images("![test](https://www.google.com) ![test2](https://www.google2.com)")),
            dict([("test", "https://www.google.com"), ("test2", "https://www.google2.com")]))
        self.assertDictEqual(dict(extract_markdown_images(
            "![test](https://www.google.com) [test1](https://www.google1.com) ![test2](https://www.google2.com)")),
                             dict([("test", "https://www.google.com"), ("test2", "https://www.google2.com")]))

    def test_extract_markdown_links(self):
        self.assertListEqual(extract_markdown_links("![test1](https://www.google1.com)"),
                             [])
        self.assertDictEqual(dict(extract_markdown_links("[test](https://www.google.com)")),
                             dict([("test", "https://www.google.com")]))
        self.assertDictEqual(
            dict(extract_markdown_links("[test](https://www.google.com) [test2](https://www.google2.com)")),
            dict([("test", "https://www.google.com"), ("test2", "https://www.google2.com")]))
        self.assertDictEqual(dict(extract_markdown_links(
            "[test](https://www.google.com) ![test1](https://www.google1.com) [test2](https://www.google2.com)")),
                             dict([("test", "https://www.google.com"), ("test2", "https://www.google2.com")]))

    def test_split_nodes_link(self):
        node = [TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )]
        node1 = [TextNode("hi there", TextType.TEXT)]
        self.assertListEqual(split_nodes_link(node),
                             [TextNode("This is text with a link ", TextType.TEXT),
                              TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                              TextNode(" and ", TextType.TEXT),
                              TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev")])
        self.assertEqual(split_nodes_link([]), [])
        self.assertEqual(split_nodes_link(node1), node1)

    def test_split_nodes_image(self):
        node = [TextNode(
            "This is text with a link ![to boot dev](https://www.boot.dev) and ![to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )]
        node1 = [TextNode("hi there", TextType.TEXT)]
        self.assertListEqual(split_nodes_image(node),
                             [TextNode("This is text with a link ", TextType.TEXT),
                              TextNode("to boot dev", TextType.IMAGE, "https://www.boot.dev"),
                              TextNode(" and ", TextType.TEXT),
                              TextNode("to youtube", TextType.IMAGE, "https://www.youtube.com/@bootdotdev")])
        self.assertEqual(split_nodes_image([]), [])
        self.assertEqual(split_nodes_image(node1), node1)

    def test_text_to_textnodes(self):
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev")
        ]
        self.assertListEqual(text_to_textnodes(
            "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"),
                             expected)

    def test_markdown_to_blocks(self):
        input = textwrap.dedent("""
        # This is a heading
        
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.
        
        * This is the first list item in a list block
        * This is a list item
        * This is another list item
        """)
        expected = ["# This is a heading","This is a paragraph of text. It has some **bold** and *italic* words inside of it.","* This is the first list item in a list block\n* This is a list item\n* This is another list item"]
        self.assertListEqual(markdown_to_blocks(input),expected)

    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# This is a heading"), "heading")
    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```This is a code```"), "code")
    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote"), "quote")
        self.assertEqual(block_to_block_type("> This is a quote\n> This is a quote"), "quote")
    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- This is a unordered_list"), "unordered_list")
        self.assertEqual(block_to_block_type("- This is a unordered_list\n- This is a unordered_list"), "unordered_list")
        self.assertEqual(block_to_block_type("* This is a unordered_list"), "unordered_list")
        self.assertEqual(block_to_block_type("* This is a unordered_list\n* This is a unordered_list"), "unordered_list")
    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. This is a ordered_list"), "ordered_list")
        self.assertEqual(block_to_block_type("1. This is a ordered_list\n2. This is a ordered_list"), "ordered_list")
        self.assertNotEqual(block_to_block_type("1. This is not a ordered_list\n3. This is not a ordered_list"), "ordered_list")
        self.assertNotEqual(block_to_block_type("2. This is not a ordered_list\n3. This is not a ordered_list"), "ordered_list")
    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), "paragraph")

    def test_markdown_to_html_node(self):
        input = textwrap.dedent("""
        # This is a heading
        
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.
        
        * This is the first list item in a list block
        * This is a list item
        * This is another list item
        
        ###### small header
        
        1. This is the first list item in a list block
        2. This is a list item
        3. This is another list item
        
        ```
        This is a code block
        ```
        
        > This is a quote
        > This is a quote2
        """)
        expexted = "<div><h1>This is a heading</h1><p>This is a paragraph of text. It has some <b>bold</b> and <i>italic</i> words inside of it.</p><ul><li>This is the first list item in a list block</li><li>This is a list item</li><li>This is another list item</li></ul><h6>small header</h6><ol><li>This is the first list item in a list block</li><li>This is a list item</li><li>This is another list item</li></ol><pre><code>\nThis is a code block\n</code></pre><blockquote>This is a quote\nThis is a quote2</blockquote></div>"

        self.assertEqual(markdown_to_html_node(input).to_html(),expexted)

    def test_extract_title(self):
        self.assertEqual(extract_title("# This is a heading"),"This is a heading")
        self.assertEqual(extract_title("# This is a heading \nsdasda\nfsdfd"),"This is a heading")
        self.assertEqual(extract_title("asda\n# This is a heading \nsdasda\nfsdfd"),"This is a heading")
        self.assertRaises(ValueError,lambda:extract_title("asda\nThis is a heading \nsdasda\nfsdfd\n\n"))


if __name__ == "__main__":
    unittest.main()
