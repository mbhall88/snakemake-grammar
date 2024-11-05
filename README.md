This repository contains a [Lark] grammar for Snakemake.

The major version of the grammar corresponds to the major version of Snakemake that it supports. Minor versions may not 
be inline with Snakemake minor versions as the grammar may not change between minor Snakemake versions. Patch versions 
are used for bug fixes and minor improvements in the grammar and have no direct relationship to Snakemake versions.

## Development

To setup the development environment, run the following commands:

```bash
uv sync
```

This will install the necessary dependencies in a virtual environment. To run the tests, use the following command:

```bash
uv run pytest
```


[Lark]: https://github.com/lark-parser/lark/