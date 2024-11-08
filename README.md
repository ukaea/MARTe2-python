# Description

The MARTe software framework is a C++ modular and multi-platform configuraton based framework for the development of real-time control system applications. You can find more on what MARTe2 is and how to get started here: [MARTe2 Documentation](https://vcis.f4e.europa.eu/marte2-docs/master/html/overview.html)

This repository provides python classes which represent MARTe2 GAMs, DataSources and applications. Alongside this it provides useful frameworks for debugging and developing applications with MARTe2.

## Intended Use

It is assumed that users have knowledge of MARTe2 and python prior to using this repository.

The repository is intended for end users to develop MARTe2 applications in python rather than text based config files, this gives the user the ability to autogenerate configurations and manage configurations in a more structured, code-based method.

This repository helps generate configuration files for MARTe2, to actually use the files you will need MARTe2 compiled alongside MARTe2-components and setup to be usable - namely with the [traditional marte shell script](https://vcis-gitlab.f4e.europa.eu/aneto/MARTe2-demos-padova/-/blob/master/Startup/Main.sh?ref_type=heads). Initial setup instructions for MARTe2 and it's dependencies can be [found here](https://vcis-gitlab.f4e.europa.eu/aneto/MARTe2-demos-padova/-/tree/master?ref_type=heads).

## Contributing & Support

When you require support please open an issue, if you would like to make adjustments to behaviour, code or additions to features, please do so as an issue and merge request.

**Note: You must comply with our guidelines as per the below.**

[Repository Guidelines](https://github.com/ukaea/MARTe2-python/blob/main/Guidelines.md)

## Installation

This repo has few dependencies and should auto install these when needed. To install the repo simply install via pip:

``` bash
pip install martepy
```

## Examples

You can find example for how to use this repository here:

[Simple Example](https://ukaea.github.io/MARTe2-python/getting_started.html)

[Water Tank Example](https://ukaea.github.io/MARTe2-python/water_tank.html)

## Support

For support on using this codebase you can refer to the documentation found here:

[User Documentation](https://ukaea.github.io/MARTe2-python/)

If you have found a bug or have a feature request then please submit an issue within this repository.

If you need additional support feel free to contact our team:

- [Edward Jones](mailto:edward.jones1@ukaea.uk)
- [Adam Stephen](mailto:adam.stephen@ukaea.uk)
- [Hudson Baker](mailto:hudson.baker@ukaea.uk)

Additionally you can utilise the MARTe Discord community server:

[MARTe Discord Server](https://discord.gg/anSXWtnprW)

## License

This software repository is provided under the European Union Public Licence as it's rooted in the use of MARTe2. You can find further details on the license [here](https://wayback.archive-it.org/12090/20200210204548/https://ec.europa.eu/idabc/en/document/7774.html).