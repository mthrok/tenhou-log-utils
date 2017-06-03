# Tenhou Log Command Line Utility

## What is this?

Tenhou Log Utils is command line tools to interact with Tenhou.net mahjong play log, written in Python.
Currently two features are available.

 - Download `mjlog` file from tenhou.net.

 - View `mjlog` file in console.


## Installation

```bash
pip install git+git://github.com/mthrok/tenhou-log-utils.git
```

## Usage

Once it's installed, you should be able to use command `tlu` (stands for Tenhou Log Utilities).
You can use `--help` to see how to use.

```bash
tlu --help
```

This should print message like the following.

```bash
usage: tlu [-h] {view,download} ...

Utility for tenhou.net log files.

positional arguments:
  {view,download}

optional arguments:
  -h, --help       show this help message and exit
```


### Download mjlog file from tenhou.net

With `download` sub command, you can download play log (`mjlog` file) from tenhou.net.

You need the log ID of the game you want to download.

Log ID is a string of form; `YYYYMMDDgm-XXXX-YYYY-ZZZZZZZZ`.

Example)

The following command will download the play log with ID `2017060314gm-0009-0000-3b2aa4ca` to `2017060314gm-0009-0000-3b2aa4ca.mjlog` in the local storage.

```bash
tlu download 2017060314gm-0009-0000-3b2aa4ca 2017060314gm-0009-0000-3b2aa4ca.mjlog
```


### View downloaded mjlog file.

You can use `view` command to see the content of a `mjlog` file.

```bash
tlu view 2017060314gm-0009-0000-3b2aa4ca.mjlog
```


## Development Installation

If you want to modify the command line, you can install in editable mode.

### 1. Clone the repository

```bash
git clone http://github.com/mthrok/tenhou-log-utils
cd tenhou-log-utils
```

### 2. Install with `-e` option.

```bash
pip install -e .
```

This will install the utility from the local repo, and you can change the behavior by modifying the content of `tenhou_log_utils` directory.