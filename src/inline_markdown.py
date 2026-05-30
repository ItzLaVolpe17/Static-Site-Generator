from textnode import TextType, TextNode
import re
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    final_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            final_list.append(node)
        else:
            
            splitted_node = node.text.split(delimiter)
            if len(splitted_node) % 2 == 0:
                raise ValueError("Invalid Markdown syntax: delimiter not closed")
            else:
                counter = 0
                for word in splitted_node:
                    if word == "":
                        counter += 1
                        continue
                    if counter % 2 == 0:
                        new_node = TextNode(word, TextType.TEXT)
                    else:
                        new_node = TextNode(word, text_type)
                    final_list.append(new_node)
                    counter += 1
    return final_list

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    final_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            final_list.append(node)
        else:
            splitted_node = extract_markdown_images(node.text)
            if len(splitted_node) == 0:
                final_list.append(node)
            else:
                remaning_text = node.text
                for alt, url in splitted_node:
                    parts = remaning_text.split(f"![{alt}]({url})", 1)
                    if parts[0] != "":
                        final_list.append(TextNode(parts[0], TextType.TEXT))
                    final_list.append(TextNode(alt, TextType.IMAGE, url))
                    remaning_text = parts[1]
                if remaning_text != "":
                    final_list.append(TextNode(remaning_text, TextType.TEXT))
    return final_list



def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    final_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            final_list.append(node)
        else:
            splitted_node = extract_markdown_links(node.text)
            if len(splitted_node) == 0:
                final_list.append(node)
            else:
                remaning_text = node.text
                for anchor, url in splitted_node:
                    parts = remaning_text.split(f"[{anchor}]({url})", 1)
                    if parts[0] != "":
                        final_list.append(TextNode(parts[0], TextType.TEXT))
                    final_list.append(TextNode(anchor, TextType.LINK, url))
                    remaning_text = parts[1]
                if remaning_text != "":
                    final_list.append(TextNode(remaning_text, TextType.TEXT))
    return final_list

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def text_to_textnode(text):
    new_text = [TextNode(text, TextType.TEXT)]
    split_bold = split_nodes_delimiter(new_text, "**", TextType.BOLD)
    split_italic = split_nodes_delimiter(split_bold, "_", TextType.ITALIC)
    split_code = split_nodes_delimiter(split_italic, "`", TextType.CODE)
    split_image = split_nodes_image(split_code)
    split_link = split_nodes_link(split_image)
    return split_link