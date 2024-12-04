# Writing Tests

The easiest way to get started is to use the interactive CLI:

```console
uv run eest make test
```

and modify the generated test module to suit your needs.

<figure class="video_container">
  <video controls="true" allowfullscreen="true">
    <source src="./img/eest_make_test.mp4" type="video/mp4">
  </video>
</figure>

For help deciding which test format to select, see [Types of Tests](./types_of_tests.md), in particular [Deciding on a Test Type](./types_of_tests.md#deciding-on-a-test-type). Otherwise, some simple test case examples to get started with are:

- [tests.berlin.eip2930_access_list.test_acl.test_access_list](../tests/berlin/eip2930_access_list/test_acl/test_access_list.md).
- [tests.istanbul.eip1344_chainid.test_chainid.test_chainid](../tests/istanbul/eip1344_chainid/test_chainid/test_chainid.md).

Please check that your code adheres to the repo's [Coding Standards](./code_standards.md) and read the other pages in this section for more background and an explanation of how to implement state transition and blockchain tests.
