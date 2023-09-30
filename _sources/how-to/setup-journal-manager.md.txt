# Setup journal-manager

Before using journal-manager we need to define an environment variable and call
`jm setup init`.

## Setting up the environment variable

The variable `JOURNAL_MANAGER_CONFIG_FOLDER` stores the directory containing
the configuration files for the journal-manager application. One can set it up
by adding the following line in the `~/.bashrc` or the correspondent file for
your terminal emulator.

```bash 
export JOURNAL_MANAGER_CONFIG_FOLDER="~/.config/journal-manager"
```

## Creating configuration files 

With the environment variable set up, we can call the `setup init` command to
create the configuration files.

```bash
$ jm setup init
$ Enter the path of your default editor: nvim

default_journal_folder=/home/my-user/.config/journal-manager/journals
default_template_folder=/home/my-user/.config/journal-manager/templates
journal_data_filepath=/home/my-user/.config/journal-manager/journal_data.toml
template_data_filepath=/home/my-user/.config/journal-manager/template_data.toml

default_text_editor_path=nvim
```

The information above is the content of the file
`${JOURNAL_MANAGER_CONFIG_FOLDER}/config/toml` created by the `setup init`
command.

- **default_journal_folder**: New journals are going to be created here by
default.
- **default_template_folder**: New journal-manager templates are going to be created
here by default.
- **journal_data_filepath**: Path to the journal configuration file. It
contains metadata of all registered journals.
- **template_data_filepath**: Path to the journal-manager templates configuration file.
It contains metadata of all registered journal-manager templates.
- **default_text_editor_path**: Path to the text editor used by default when
editing a journal, for example.

```{tip}
To update the default text editor, type `jm setup init` again.
```

## Updating journal-manager configuration

After `jm setup init` is called, you can manually edit the configuration files.
Type `jm setup` to open the `${JOURNAL_MANAGER_CONFIG_FOLDER}/config.toml`. 

```{tip}
After creating journals you can also manually update the `journal_data.toml`
file by typing the command `jm setup --journal`.

Similarly, you can also edit `template_data.toml` with `jm setup --template`
```
