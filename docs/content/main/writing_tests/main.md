+++
title = 'Writing Tests'
date = 2025-07-09T12:42:33Z
draft = false
[menu]
  [menu.main]
    name = 'Writing Tests'
    weight = 12

+++

The easiest way to get started is to use the interactive CLI:

```console
uv run eest make test
```

and modify the generated test module to suit your needs.

![Gif that shows how to create a test in EEST](/images/writing_tests/eest_make_test.gif)

For help deciding which test format to select, see [Types of Tests]({{< ref "types_of_tests.md" >}}), in particular [Deciding on a Test Type]({{< ref "types_of_tests.md#deciding-on-a-test-type" >}}).

## Key Resources

- [Coding Standards]({{< ref "code_standards.md#code-standards" >}}) - Code style and standards for this repository
- [Adding a New Test]({{< ref "adding_a_new_test.md" >}}) - Step-by-step guide to adding new tests
- [Writing a New Test]({{< ref "writing_a_new_test.md" >}}) - Detailed guide on writing different test types
- [Using and Extending Fork Methods]({{< ref "fork_methods.md" >}}) - How to use fork methods to write fork-adaptive tests
- [Porting tests]({{< ref "porting_legacy_tests.md" >}}): A guide to porting [ethereum/tests](https://github.com/ethereum/tests) to EEST.

Please check that your code adheres to the repo's coding standards and read the other pages in this section for more background and an explanation of how to implement state transition and blockchain tests.
