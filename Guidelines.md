# Guidelines

## Community Guidelines

This is a community provided Custom Device and we prescribe to the ideals and concepts outlined in the Python Software Foundation Code of Conduct. By contributing or using this repository you are also prescribing to behave accordingly as set out in the code of conduct within this respository.

https://policies.python.org/python.org/code-of-conduct/

## Contributor Guidelines

If you believe you have found an issue in the software, please report this as an issue. If you believe you have fixed an issue then open a issue as well as a merge request.

**This repository is not intended to be officially supported by UKAEA, if you want an issue fixed, the best way to do so is to create the fix yourself and then submit the fix as a merge request. We will try to maintain support as best way can but provide no gauranetees onto fixing an issue or a timeframe to do so.**

## Style Guidelines

The style of how this repository is coded is strictly controlled by the pipeline process with pylint verifying code submissions. The general rules of pylint for our repository are:

- No line longer than 100 characters: Use multi-line methods in python to avoid these and try to break out code actions to avoid long lines.

- No overly nested branches of logic: Try to avoid this where possible however it is understood this can be required so it is allowed to override the warning with pylint ignore commenting.

- No more than 15 local variables in a function.

- All classes, functions and files must have comments providing definitions.

For naming conventions we have:

- Class: PascalCase
- Constants: UPPERCASE
- Function/Method: camelCase
- Function Arguments: snake_case
- Variable: Any
- Attribute: Any

**If you add new code then it is expected that you build a corresponding set of pytests to ensure that it is functional. This is useful in iterating software to ensure that this code is always functional without requiring developer time successively.**