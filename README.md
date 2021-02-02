# Repository Gardener

[![Actions Status][gh-actions-badge]][gh-actions]

The repository gardener maintains code samples by running some automatable
tasks. For example, it can automatically update dependencies and then after
running tests to ensure they still work, send a Pull Request for the update.

## Example

The following commands will clone the java-docs-samples repository and update
its dependencies to the latest versions.

For Java, we need to also clone the `java-repo-tools` repository to get the
latest version updater configuration.

```shell
source set-env.sh \
  && git clone https://github.com/GoogleCloudPlatform/java-repo-tools.git
  && ./clone-and-checkout.sh -b dpebot-updatedeps GoogleCloudPlatform/java-docs-samples \
  && ( \
    cd repo-to-update \
    && ../use-latest-deps-java.sh -d GoogleCloudPlatform/java-docs-samples
 )
```

The `-d` option in `use-latest-deps-java.sh` is to do a dry run (don't commit
or push). Remove `-d` to actually push and send PR.

## Contributing changes

* See [CONTRIBUTING.md](CONTRIBUTING.md)

## Licensing

* See [LICENSE](LICENSE)

## Disclaimer

This is not an official Google product or sample.

## Adding the bot to your repository (Googlers only)

A hosted version of the bot is [available](https://goto.google.com/dpebot) for Googlers.

[gh-actions]: https://github.com/GoogleCloudPlatform/repository-gardener/actions
[gh-actions-badge]: https://github.com/GoogleCloudPlatform/repository-gardener/workflows/CI%20Tests/badge.svg
