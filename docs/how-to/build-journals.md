# Build journals

The `build` command creates a static web page for a set of registered
journals plus an index page.

## Active and Registered journals 

In order to be built, a journal must be registered. All newly created 
journals are registered automatically, but if you wish to not track a 
journal anymore you need to deregister it.

```bash
$ jm journal list
nlp:/home/my-user/.config/journal-manager/journals/nlp
statistics:/home/my-user/.config/journal-manager/journals/statistics

$ jm journal deregister statistics
$ jm journal list 
nlp:/home/my-user/.config/journal-manager/journals/nlp
```

```{important}
The `deregister` command will not remove any file in your system 
```

The `build` command will build active and inactive journals though. We set
a journal as inactive to flag that we are not going to update it very often, 
and that it is in archived state. The `build` command uses this information
to create a list of `active` and `archived` journals.

## Build journals

The simplest way to execute the `build` command is the following:

```bash
$ jm journal build
```

All registered journals plus an index page are going to be build in a folder 
called `site` located in the current directory. Inside `site` there will be 
one folder for each journal.

```{tip}
If you don't want to build the index page, pass the flag --do-not-build-index.
```

You can instruct the `build` command to build in a specific directory using the 
flag `--build-location` and only a set of journals with the flag `--journal-name`
or `--jn`.

```bash
$ jm journal build --build-location ~/my-build-journals --jn nlp statistics
```

```{tip}
Instead of passing the journal name to the `build` command, you can also pass the 
journal location using the flag `--journal-location`.
```

### HTTP testing server 

To test your build journals you can pass the flag `--with-http-server`. This flag 
creates a simple http server to serve the created files. You need to have [nodejs](https://nodejs.org/en)
and [entr](https://github.com/eradman/entr/) installed to run this feature.

If the `--with-http-server` is passed, two additional directories will be created 
in the `--build-location` folder:

- http-server: a basic nodejs http-server.
- file-monitor: a script based on `entry` to monitor files in the `site` folder.

### Build instructions file 

An alternative way to call the `build` command is passing a `toml` build-instruction file.
Here it is its dataclass definition.

```python
class BuildInstructions(TomlDataClassIO):
    build_location: Optional[str] = None

    build_index: bool = True
    with_http_server: bool = False

    journals_names_to_build: Optional[List[str]] = None
    journals_locations_to_build: Optional[List[str]] = None
    include_all_folder: Optional[str] = None
```

Below it is an example in `toml` format:

```toml
build_location = "~/my-build-journals"
build_index = true
include_all_folder = ~/.config/journal-manager/journals
```

```{tip}
The `include_all_folder` parameter holds a journal directory in which all journals should be built.
```

