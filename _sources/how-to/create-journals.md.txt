# Create journals

You can create journals from scratch, using a journal-manager template or register an
existing journal.

## Create a new journal 

Use the command `journal create` to create a new journal.

```bash
$ jm journal create "nlp"
```

```{tip}
You can also type `jm j c "nlp"` to create a new journal.
```

This command it is just a wrap around `mkdocs new`. The new journal is created
in the directory given by `default_journal_folder` in the configuration
file. You can also indicate a new location by passing the parameter `--journal-folder`

```bash
$ jm journal create "nlp" --journal-folder "~/my-journals"
```

## Create a journal from a journal-manager template

A journal-manager template is a directory containing at least one file:
`mkdocs.tpl.yml`. This file has the same structure of the `mkdocs.yml` but with
jinja2 placeholders. Here it is an example:

```yml
site_name: {{journal.title}}
theme:
  name: material
  custom_dir: overrides
  features:
    - search.suggest
    - search.highlight

plugins:
  - search


markdown_extensions:
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.details
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tilde
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg


extra_javascript:
  - javascripts/mathjax.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

You can set up your template to use a specific MkDocs theme and select the list
of active plugins. The template can render metadata of the journal such as the
`title` or its `name`.

After creating a journal-manager template, you should register it using the `template
register` command.

```bash
$ jm template register "~/my-template"
```

Notice that we pass a directory to the `template register` command. That's
because the full content of this directory will be copied when generating a
journal according with this template. 

This can be useful if one has custom assets such as images and scripts or if
one wants to override or extend a MkDocs theme by creating the `overrides`
folder. More information about MkDocs theme customization can be found
[here](https://squidfunk.github.io/mkdocs-material/customization/).

```{tip}
A popular journal-manager template is the [quick-notes-template](). This template adds a
dynamic functionality to the static MkDocs' pages. One can update the journal
by pushing content online. More information can be found in our tutorial:
[Setting up a personal journal server]()
```

## Register an existing journal

You may have a MkDocs journal already. To start managing it from
journal-manager you just need to register it.

```bash
$ jm journal register "~/my-journal-location"
```

If no title is given, the journal will have the title of the folder it contains
it.

```{tip}
You can give a title for your journal by passing the parameter --title.
```


