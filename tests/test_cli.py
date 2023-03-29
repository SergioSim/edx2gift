"""Tests for edx2gift cli."""

import pytest
from click.testing import CliRunner

from edx2gift.cli import cli, convert_edx_2_gift, escape_text


@pytest.mark.parametrize(
    "text,expected",
    [
        (" \n  text should be stripped  \n ", "text should be stripped"),
        (":={} should be escaped", "\\:\\=\\{\\} should be escaped"),
    ],
)
def test_cli_escape_text(text, expected):
    """Tests the escape_text function, given input, should produce expected result."""

    assert escape_text(text) == expected


def test_cli_convert_edx_2_gift():
    """Tests the convert_edx_2_gift function, given valid content, should yield the
    expected result."""
    xml = """
        <problem>
        <p>Multiple choice response question prompt ?</p>
        <multiplechoiceresponse>
            <choicegroup type="MultipleChoice" label="IGNORED">
                <choice correct="true">True</choice>
                <choice correct="false">False</choice>
            </choicegroup>
        </multiplechoiceresponse>

        <p>Choice response question prompt?</p>
        <choiceresponse>
        <checkboxgroup>
            <choice correct="false">False </choice>
            <choice correct="true">True 1</choice>
            <choice correct="true">True 2</choice>
        </checkboxgroup>
        </choiceresponse>

        <p>Numerical response prompt?</p>
        <numericalresponse answer="1.2">
        <responseparam type="tolerance" default=".1" />
        <formulaequationinput label="IGNORED" />
        </numericalresponse>
        <h1>UNSUPPORTED</h1>
        </problem>
    """

    expected = """::Q1::Multiple choice response question prompt ?{
            =True
            ~False
        }

        ::Q2::Choice response question prompt?{
            ~%-1.00000%False
            ~%0.50000%True 1
            ~%0.50000%True 2
        }

        ::Q3::Numerical response prompt?{#
            =%100%1.2:0.1
        }
    """
    expected = expected.replace(" " * 12, "\t").replace(" " * 4, "")
    assert "".join(convert_edx_2_gift(xml)) == expected


def test_cli_cli(fs):
    """Tests the cli function."""
    # pylint: disable=invalid-name

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 2
    expected = """Usage: cli [OPTIONS] EDX_XML_FILE
    Try 'cli --help' for help.

    Error: Missing argument 'EDX_XML_FILE'.
    """
    assert result.output == expected.replace(" " * 4, "")

    fs.create_file("foo.xml", contents="<root><p>foo</p></root>")
    result = runner.invoke(cli, ["foo.xml"])
    assert result.output == "::Q1::foo{"
