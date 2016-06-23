# Repository Gardener

[![Build Status](https://travis-ci.org/GoogleCloudPlatform/repo-gardener.svg)](https://travis-ci.org/GoogleCloudPlatform/repo-gardener)

The repository gardener maintains code samples by running some automatable
tasks. For example, it can automatically update dependencies and then after
running tests to ensure they still work, send a Pull Request for the update.

## Example

The following commands will clone the java-docs-samples repository and update
its dependencies to the latest versions. (Assumes that java-repo-tools is
already cloned to the `~/java-repo-tools` directory.)

```shell
source set-env.sh \
  && ./clone-and-checkout.sh java-docs-samples \
  && ( \
    cd repo-to-update \
    && ../use-latest-deps-java.sh \
      -d java-docs-samples \
      -Dmaven.version.rules=file://$HOME/src/java-repo-tools/versions-rules.xml
 )
```

## Contributing changes

* See [CONTRIBUTING.md](CONTRIBUTING.md)

## Licensing

* See [LICENSE](LICENSE)

## Disclaimer

This is not an official Google product or sample.
