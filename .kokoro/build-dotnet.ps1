# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

get-command choco -ErrorAction Stop
choco list -li | Tee-Object -Variable chocoList
$chocoPackages = ($chocoList) -join ' '

# Install dotnet
if (-not $chocoPackages.Contains('Microsoft .NET Core SDK - 2.1.4')) {
  choco install -y --sxs dotnetcore-sdk --version 2.1.401
}

dotnet --info

if (-not $Dir) {
  $Dir = "$PSScriptRoot\..\env"
}

# Install dotnet-outdated and add it to PATH
$installDir = Join-Path $Dir 'install'
dotnet tool install --tool-path $installDir\dotnet-tools dotnet-outdated
$env:Path = @("$installDir\dotnet-tools", $env:Path) -join ';'

# Clone the target repo and checkout a new branch.
if (-not $env:DPEBOT_BRANCH) {
  sh .\clone-and-checkout.sh $env:DPEBOT_REPO
} else {
  sh .\clone-and-checkout.sh -b $env:DPEBOT_BRANCH $env:DPEBOT_REPO
}

# Update dependencies in the repo and send PR to github.
cd repo-to-update
sh ..\use-latest-deps-dotnet.sh "$env:DPEBOT_REPO"
