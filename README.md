# Edx2Gift

Converts edX quizzes in XML format to Moodle GIFT format.

> **Warning**
> This project is not production ready and doesn't support all edX question types / formats.

## Supported format

We expect that the edX quiz XML file follows the following format:

```XML
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
```

## Supported edX question types

- multiplechoiceresponse
- choiceresponse
- numericalresponse


## Getting started

### Running the edx2gift CLI using Make and Docker compose

To try out the CLI, clone this repository, navigate to the project root directory and
install it with:

```bash
$ make bootstrap
```

Next, place an XML file containing the edX quiz in the same directory.
Finally run the edx2gift CLI with:

```bash
$ bin/edx2gift edX_XML_file_name.xml
```

The command should respond by printing the converted quiz to standard output.

It's also possible to redirect the output to a file; e.g.:

```bash
$ bin/edx2gift edX_XML_file_name.xml > gift_file_ name.gift
```


### Running the edx2gift API server (web interface)

To try out the API server, as with the CLI, the first step is to clone this repository,
navigate to the project root directory and install it:

> **Note**
> You can skip this part if you have already done it previously.

```bash
$ make bootstrap
```

The installation command creates a `.env` file which lets you define the basic auth user
credentials.
Update these credentials if you want to password protect the API conversion route.

> **Note**
> The default credentials are just empty strings.

Next, start the API server (as a background task) with:

```bash
make run
```

Finally, using your browser of choice, navigate to `http://localhost:8100`.
Its a basic web interface that lets you paste the edx XML quiz and convert it to GIFT.
