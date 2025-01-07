import os
import shutil

from textnode import extract_title
from textnode import markdown_to_html_node


def main():
    clear_public()
    generate_pages("content", "public")

def generate_pages(source, destination):
    for file in os.listdir(source):
        if os.path.isfile(os.path.join(source, file)):
            if file.endswith(".md"):
                generate_page(
                    os.path.join(source, file),
                    "template.html",
                    os.path.join(destination, file.replace(".md", ".html")),
                )
        if os.path.isdir(os.path.join(source, file)):
            generate_pages(os.path.join(source, file), os.path.join(destination, file))


def clear_public():
    print(f"removing public folder")
    shutil.rmtree("public", ignore_errors=True)
    print(f"making public folder")
    os.mkdir("public")
    print(f"copying files")
    copy_tree("static", "public")

def copy_tree(source, destination):
    for item in os.listdir(source):
        if os.path.isdir(os.path.join(source, item)):
            os.mkdir(os.path.join(destination, item))
            copy_tree(os.path.join(source, item), os.path.join(destination, item))
        if os.path.isfile(os.path.join(source, item)):
            print(f"Copying {os.path.join(source, item)} to {os.path.join(destination, item)}")
            shutil.copy(os.path.join(source, item), destination)

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        from_text = f.read()
    with open(template_path, "r") as f:
        template_text = f.read()
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(
            template_text.replace("{{ Title }}", extract_title(from_text))
            .replace("{{ Content }}", markdown_to_html_node(from_text).to_html())
        )

main()
