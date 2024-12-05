# EEST `fill`

```mermaid
%%{init: {'theme':'dark'}}%%
flowchart LR
  style input_or_output            stroke: #18ACD3, stroke-width:4px
  style fixtures                   stroke: #18ACD3, stroke-width:4px
  style tests-EIP-123              stroke: #18ACD3, stroke-width:4px

  style test_infra_exe             stroke: #5AB56F, stroke-width:4px
  style fill                       stroke: #5AB56F, stroke-width:4px

  style exe_under_test             stroke: #FFEC5D, stroke-width:4px
  style t8n                        stroke: #5AB56F, stroke-width:4px

  style test_source                  fill: #343A40, stroke-width:4px  



  fixtures(<code>./fixtures/**/*.json</code>)

  subgraph "ethereum/execution-spec-tests"
    subgraph "Test Filler Framework"
        subgraph test_source["Python Test Cases"]
          tests-EIP-123(<code>./tests/**/*.py</code>)
        end
        fill(<code>$ fill ./tests/</code>)
    end
  end


  t8n(<code>evm t8n</code>)


  subgraph Legend
    input_or_output("Input or Output")
    test_infra_exe("Test Infra Executable")
    exe_under_test("Executable under Test")
  end

  t8n            <.-> fill
  tests-EIP-123    --> fill
  fill             --> |output| fixtures
```

```mermaid
%%{init: {'theme':'dark', 'flowchart': {'useMaxWidth': true}}}%%
flowchart LR
  style input_or_output stroke:#18ACD3,stroke-width:4px
  style fixtures stroke:#18ACD3,stroke-width:4px
  style tests-EIP-123 stroke:#18ACD3,stroke-width:4px

  style test_infra_exe stroke:#5AB56F,stroke-width:4px
  style fill stroke:#5AB56F,stroke-width:4px

  style exe_under_test stroke:#FFEC5D,stroke-width:4px
  style t8n stroke:#5AB56F,stroke-width:4px

  style test_source fill:#343A40,stroke-width:4px

  fixtures(<code>./fixtures/**/*.json</code>)

  subgraph "ethereum/execution-spec-tests&nbsp;&nbsp;"
    subgraph "Test Filler Framework&nbsp;&nbsp;"
      subgraph test_source["Python Test Cases&nbsp;&nbsp;"]
        tests-EIP-123(<code>./tests/**/*.py</code>)
      end
      fill(<code>$ fill ./tests/</code>)
    end
  end

  t8n(<code>evm t8n</code>)

  subgraph Legend
    input_or_output("Input or Output")
    test_infra_exe("Test Infra Executable")
    exe_under_test("Executable under Test")
  end

  t8n --> fill
  tests-EIP-123 --> fill
  fill --> |output| fixtures
```