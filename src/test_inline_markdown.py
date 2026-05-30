import unittest
from textnode import TextNode, TextType
from inline_markdown import split_nodes_delimiter, extract_markdown_links, extract_markdown_images, split_nodes_image, split_nodes_link, text_to_textnode


class TestSplitNodesDelimiterBasic(unittest.TestCase):
    """Casi base: funzionamento normale."""

    def test_single_bold_word(self):
        node = TextNode("Hello **world** here", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(result), 3)  # ← era 2
        self.assertEqual(result[0].text, "Hello ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "world")
        self.assertEqual(result[1].text_type, TextType.BOLD)
        self.assertEqual(result[2].text, " here")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_single_italic_word(self):
        node = TextNode("This is *italic* text", TextType.TEXT)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(result[0].text, "This is ")
        self.assertEqual(result[1].text, "italic")
        self.assertEqual(result[1].text_type, TextType.ITALIC)
        self.assertEqual(result[2].text, " text")

    def test_single_code_span(self):
        node = TextNode("Use `print()` here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result[1].text, "print()")
        self.assertEqual(result[1].text_type, TextType.CODE)

    def test_multiple_delimiters_in_one_node(self):
        """Due occorrenze del delimiter nella stessa stringa."""
        node = TextNode("**a** and **b**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        texts = [(n.text, n.text_type) for n in result]
        self.assertIn(("a", TextType.BOLD), texts)
        self.assertIn(("b", TextType.BOLD), texts)

    def test_delimiter_at_start(self):
        """Delimiter che apre la stringa — la parte TEXT iniziale è vuota e va saltata."""
        node = TextNode("**bold** then text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        # Il chunk vuoto prima di **bold** deve essere ignorato
        self.assertTrue(all(n.text != "" for n in result))
        self.assertEqual(result[0].text, "bold")
        self.assertEqual(result[0].text_type, TextType.BOLD)

    def test_delimiter_at_end(self):
        """Delimiter che chiude la stringa — la parte TEXT finale è vuota e va saltata."""
        node = TextNode("text then **bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertTrue(all(n.text != "" for n in result))
        self.assertEqual(result[-1].text, "bold")
        self.assertEqual(result[-1].text_type, TextType.BOLD)

    def test_no_delimiter_present(self):
        """Nessun delimiter: restituisce un unico nodo TEXT invariato."""
        node = TextNode("plain text no markup", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "plain text no markup")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_multiple_input_nodes(self):
        """Lista con più nodi in input vengono tutti processati."""
        nodes = [
            TextNode("first **one**", TextType.TEXT),
            TextNode("second **two**", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        bold_nodes = [n for n in result if n.text_type == TextType.BOLD]
        self.assertEqual(len(bold_nodes), 2)
        self.assertEqual(bold_nodes[0].text, "one")
        self.assertEqual(bold_nodes[1].text, "two")


class TestSplitNodesDelimiterNonTextNodes(unittest.TestCase):
    """Nodi non-TEXT devono passare inaltarati."""

    def test_bold_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], node)

    def test_italic_node_passes_through(self):
        node = TextNode("already italic", TextType.ITALIC)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], node)

    def test_code_node_passes_through(self):
        node = TextNode("already code", TextType.CODE)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], node)

    def test_mixed_text_and_non_text_nodes(self):
        """Nodi TEXT vengono splittati, non-TEXT restano invariati."""
        nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode("has **markup** here", TextType.TEXT),
            TextNode("already italic", TextType.ITALIC),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        # Il primo e l'ultimo passano invariati
        self.assertEqual(result[0].text, "already bold")
        self.assertEqual(result[0].text_type, TextType.BOLD)
        self.assertEqual(result[-1].text, "already italic")
        self.assertEqual(result[-1].text_type, TextType.ITALIC)
        # In mezzo ci sono i nodi splittati da "has **markup** here"
        middle = result[1:-1]
        bold_nodes = [n for n in middle if n.text_type == TextType.BOLD]
        self.assertEqual(len(bold_nodes), 1)
        self.assertEqual(bold_nodes[0].text, "markup")

    def test_empty_input_list(self):
        result = split_nodes_delimiter([], "**", TextType.BOLD)
        self.assertEqual(result, [])


class TestSplitNodesDelimiterValueError(unittest.TestCase):
    """Delimiter non chiuso deve sollevare ValueError."""

    def test_unclosed_delimiter_raises(self):
        node = TextNode("Hello **world", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_single_delimiter_raises(self):
        """Una sola occorrenza del delimiter = non chiuso."""
        node = TextNode("only one `backtick here", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_three_delimiters_raises(self):
        """Tre delimiters = il secondo è aperto e mai chiuso."""
        node = TextNode("**a** and **b", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_error_message_is_descriptive(self):
        """Il messaggio dell'eccezione deve contenere informazioni utili."""
        node = TextNode("unclosed **delimiter", TextType.TEXT)
        with self.assertRaises(ValueError) as ctx:
            split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertIn("delimiter", str(ctx.exception).lower())

    def test_unclosed_raises_before_processing_valid_node(self):
        """Il ValueError viene sollevato anche se altri nodi nella lista sono validi."""
        nodes = [
            TextNode("valid **text** here", TextType.TEXT),
            TextNode("unclosed **delimiter", TextType.TEXT),
        ]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)


class TestSplitNodesDelimiterWhitespace(unittest.TestCase):
    """Casi limite con stringhe vuote e whitespace."""

    def test_empty_string_node_skipped(self):
        """Un chunk vuoto prodotto dallo split non genera nodi."""
        node = TextNode("**bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertTrue(all(n.text != "" for n in result))

    def test_whitespace_only_inside_delimiter_is_preserved(self):
        """Spazi dentro il delimiter: il nodo viene creato con quel contenuto."""
        node = TextNode("before ** ** after", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        styled = [n for n in result if n.text_type == TextType.BOLD]
        self.assertEqual(len(styled), 1)
        self.assertEqual(styled[0].text, " ")

    def test_whitespace_only_outside_delimiter(self):
        """Spazi fuori dal delimiter producono un nodo TEXT con solo spazi."""
        node = TextNode(" **bold** ", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        text_nodes = [n for n in result if n.text_type == TextType.TEXT]
        # Gli spazi esterni non sono stringhe vuote, devono essere mantenuti
        self.assertTrue(all(n.text != "" for n in result))
        for tn in text_nodes:
            self.assertEqual(tn.text.strip(), "")  # contengono solo whitespace

    def test_adjacent_delimiters_empty_content(self):
        """Delimiter adiacenti (contenuto vuoto): il nodo interno viene saltato."""
        node = TextNode("text `` more", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        # Nessun nodo con testo vuoto
        self.assertTrue(all(n.text != "" for n in result))

    def test_node_with_only_delimiter(self):
        """Stringa composta unicamente da delimiter apertura+chiusura."""
        node = TextNode("****", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        # Contenuto interno è vuota → saltato, risultato è lista vuota
        self.assertEqual(result, [])

class TestExtractMarkdown(unittest.TestCase):
    
    def test_extract_markdown_images_single(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "![cat](https://example.com/cat.png) and ![dog](https://example.com/dog.png)"
        )
        self.assertListEqual(
            [("cat", "https://example.com/cat.png"), ("dog", "https://example.com/dog.png")],
            matches
        )

    def test_extract_markdown_images_no_images(self):
        matches = extract_markdown_images("This is plain text with no images")
        self.assertListEqual([], matches)

    def test_extract_markdown_images_ignores_links(self):
        matches = extract_markdown_images(
            "This is a [link](https://example.com) not an image"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_links_single(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev)"
        )
        self.assertListEqual([("link", "https://boot.dev")], matches)

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "Go to [Google](https://google.com) or [GitHub](https://github.com)"
        )
        self.assertListEqual(
            [("Google", "https://google.com"), ("GitHub", "https://github.com")],
            matches
        )

    def test_extract_markdown_links_no_links(self):
        matches = extract_markdown_links("Just some plain text")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_ignores_images(self):
        matches = extract_markdown_links(
            "This is an ![image](https://example.com/cat.png) not a link"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_mixed(self):
        matches_images = extract_markdown_images(
            "A ![photo](https://img.com/a.png) and a [link](https://boot.dev)"
        )
        matches_links = extract_markdown_links(
            "A ![photo](https://img.com/a.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual([("photo", "https://img.com/a.png")], matches_images)
        self.assertListEqual([("link", "https://boot.dev")], matches_links)


class TestSplitNodesImage(unittest.TestCase):

    def test_single_image(self):
        node = TextNode("![alt](https://img.com/pic.png)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("alt", TextType.IMAGE, "https://img.com/pic.png")
        ])

    def test_text_before_and_after(self):
        node = TextNode("before ![alt](https://img.com/pic.png) after", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [
            TextNode("before ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "https://img.com/pic.png"),
            TextNode(" after", TextType.TEXT),
        ])

    def test_no_images(self):
        node = TextNode("testo senza immagini", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_non_text_node_passed_through(self):
        node = TextNode("alt", TextType.IMAGE, "https://img.com/pic.png")
        result = split_nodes_image([node])
        self.assertEqual(result, [node])


class TestSplitNodesLink(unittest.TestCase):

    def test_single_link(self):
        node = TextNode("[boot dev](https://www.boot.dev)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("boot dev", TextType.LINK, "https://www.boot.dev")
        ])

    def test_text_before_and_after(self):
        node = TextNode("visita [boot dev](https://www.boot.dev) oggi", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [
            TextNode("visita ", TextType.TEXT),
            TextNode("boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" oggi", TextType.TEXT),
        ])

    def test_no_links(self):
        node = TextNode("testo senza link", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_non_text_node_passed_through(self):
        node = TextNode("boot dev", TextType.LINK, "https://www.boot.dev")
        result = split_nodes_link([node])
        self.assertEqual(result, [node])


    def test_full_example(self):
            text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
            result = text_to_textnode(text)
            self.assertEqual(result, [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ])

    def test_plain_text(self):
        text = "testo senza formattazione"
        result = text_to_textnode(text)
        self.assertEqual(result, [
            TextNode("testo senza formattazione", TextType.TEXT)
        ])

    def test_only_bold(self):
        text = "**solo bold**"
        result = text_to_textnode(text)
        self.assertEqual(result, [
            TextNode("solo bold", TextType.BOLD)
        ])

if __name__ == "__main__":
    unittest.main()