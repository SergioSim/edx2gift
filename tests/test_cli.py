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
        </problem>
    """

    expected = """::Q1::[html]<p>Multiple choice response question prompt ?</p>{
            =True
            ~False
        }

        ::Q2::[html]<p>Choice response question prompt?</p>{
            ~%-100%False
            ~%50%True 1
            ~%50%True 2
        }

        ::Q3::[html]<p>Numerical response prompt?</p>{#
            =%100%1.2:0.1
        }
    """
    expected = expected.replace(" " * 12, "\t").replace(" " * 4, "")
    assert "".join(convert_edx_2_gift(xml)) == expected


def test_cli_convert_edx_2_gift_with_nested_problem():
    """Tests the convert_edx_2_gift function, given a nested problem, should yield the
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

        <problem>
            <p>Multiple choice</p>
            <p>question prompt ?</p>
            <multiplechoiceresponse>
                <choicegroup type="MultipleChoice" label="IGNORED">
                    <choice correct="true">True</choice>
                    <choice correct="false">False</choice>
                </choicegroup>
            </multiplechoiceresponse>
        </problem>

        <p>Choice response question prompt?</p>
        <choiceresponse>
        <checkboxgroup>
            <choice correct="false">False </choice>
            <choice correct="true">True 1</choice>
            <choice correct="true">True 2</choice>
        </checkboxgroup>
        </choiceresponse>

        </problem>
    """

    expected = """::Q1::[html]<p>Multiple choice response question prompt ?</p>{
            =True
            ~False
        }

        ::Q2::[html]<p>Multiple choice</p><p>question prompt ?</p>{
            =True
            ~False
        }

        ::Q3::[html]<p>Choice response question prompt?</p>{
            ~%-100%False
            ~%50%True 1
            ~%50%True 2
        }
    """
    expected = expected.replace(" " * 12, "\t").replace(" " * 4, "")
    assert "".join(convert_edx_2_gift(xml)) == expected


def test_cli_convert_edx_2_gift_producing_invalid_results():
    """Tests the convert_edx_2_gift function, given a not supported problem type, should
    yield an invalid result."""
    # Converting quizzes containg images is not supported.
    xml = """
        <problem>
        <p>Choice response question prompt?</p>
        <choiceresponse>
        <checkboxgroup>
            <choice correct="false"><img src="file_1"/></choice>
            <choice correct="true"><img src="file_2"/></choice>
        </checkboxgroup>
        </choiceresponse>
        </problem>
    """

    expected = """::Q1::[html]<p>Choice response question prompt?</p>{
            ~%-100%
            ~%100%
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

    xml = """
        <problem>
        <p>Numerical response prompt?</p>
        <numericalresponse answer="1.2">
        <responseparam type="tolerance" default=".1" />
        <formulaequationinput label="IGNORED" />
        </numericalresponse>
        </problem>
    """

    expected = """::Q1::[html]<p>Numerical response prompt?</p>{#
            =%100%1.2:0.1
        }
    """
    expected = expected.replace(" " * 12, "\t").replace(" " * 4, "")

    fs.create_file("foo.xml", contents=xml)
    result = runner.invoke(cli, ["foo.xml"])
    assert result.output == expected
