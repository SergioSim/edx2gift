"""Edx2Gift CLI entrypoint."""

import logging
from typing import Iterator, TextIO

import click
from defusedxml.ElementTree import fromstring

logger = logging.getLogger(__name__)


def escape_text(text: str) -> str:
    """Escapes special characters that are not allowed in GIFT format."""
    for char in ":{}=":
        text = text.replace(char, f"\\{char}")
    return text.strip()


def convert_edx_2_gift(content: str) -> Iterator[str]:
    """Parses content (edX XML formatted exercises) and yields Moodle GIFT format."""
    count = 1
    for child in fromstring(content):
        if child.tag == "p":
            newline = "" if count == 1 else "\n"
            yield f"{newline}::Q{count}::{escape_text(child.text)}{{"
            count += 1
        elif child.tag == "multiplechoiceresponse":
            yield "\n"
            for choice in child.findall("choicegroup/choice"):
                sign = "=" if choice.get("correct") == "true" else "~"
                yield f"\t{sign}{escape_text(choice.text)}\n"
            yield "}\n"
        elif child.tag == "choiceresponse":
            yield "\n"
            correct_count = 0
            choices = []
            for choice in child.findall("checkboxgroup/choice"):
                if choice.get("correct") == "true":
                    correct_count += 1
                choices.append(choice)
            false_count = len(choices) - correct_count
            false_count = false_count if false_count else 1
            true_ratio = f"{1.0 / correct_count:.5f}"
            false_ratio = f"{- 1.0 / false_count:.5f}"
            for choice in choices:
                ratio = true_ratio if choice.get("correct") == "true" else false_ratio
                yield f"\t~%{ratio}%{escape_text(choice.text)}\n"
            yield "}\n"
        elif child.tag == "numericalresponse":
            yield "#\n"
            tolerance = ""
            params = child.find("responseparam")
            if params is not None:
                if params.get("type") == "tolerance":
                    tolerance = f":0{params.get('default')}"
            yield f"\t=%100%{escape_text(child.get('answer'))}{tolerance}\n"
            yield "}\n"
        else:
            logger.warning("Unsupported question %s", child)


@click.command()
@click.argument("EDX_XML_FILE", type=click.File(encoding="utf-8"))
def cli(edx_xml_file: TextIO) -> None:
    """Converts an edX XML formatted exercises file into Moodle GIFT format.

    EDX_XML_FILE: The path to the edX XML formatted excercises file to convert.
    """
    for line in convert_edx_2_gift(edx_xml_file.read()):
        click.echo(line, nl=False)
