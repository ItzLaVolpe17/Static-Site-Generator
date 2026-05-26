import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestTextNode(unittest.TestCase):
    def test_props_none(self):
        node = HTMLNode("p", "hello")
        self.assertEqual(node.props_to_html(), "")

    def test_props_one(self):
        node = HTMLNode("a", "click", props={"href": "https://www.google.com"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com"')

    def test_props_two(self):
        node = HTMLNode("a", "click", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_no_tag(self):
        node = LeafNode(None, "raw text", None)
        self.assertEqual(node.to_html(), "raw text")
        
    def test_parent_with_children(self):
        node = ParentNode("p", [LeafNode("b", "Bold text"), LeafNode(None, "Normal text")])
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text</p>")

    def test_parent_nested(self):
        inner = ParentNode("b", [LeafNode(None, "Bold")])
        outer = ParentNode("p", [inner, LeafNode(None, " text")])
        self.assertEqual(outer.to_html(), "<p><b>Bold</b> text</p>")

    def test_parent_with_props(self):
        node = ParentNode("a", [LeafNode(None, "Click")], {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click</a>')

if __name__ == "__main__":
    unittest.main()