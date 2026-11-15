#!/bin/bash
# 在 ubuntu:20.04 容器里跑：AOSP 9 / twrp-9.0 需要 python2 和 JDK8，22.04 已没有 python2。
set -eux

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
    openjdk-8-jdk git curl ca-certificates bc bison build-essential ccache flex \
    g++-multilib gcc-multilib gperf imagemagick lib32ncurses5-dev lib32readline-dev \
    lib32z1-dev libelf-dev liblz4-tool libncurses5 libncurses5-dev libsdl1.2-dev \
    libssl-dev libxml2 libxml2-utils lzop pngcrush rsync schedtool squashfs-tools \
    xsltproc zip zlib1g-dev unzip python2 python-is-python2

python --version || true
java -version || true

# repo 工具
mkdir -p /usr/local/bin
curl -s https://storage.googleapis.com/git-repo-downloads/repo > /usr/local/bin/repo
chmod a+x /usr/local/bin/repo

git config --global user.name "ci-builder"
git config --global user.email "ci@localhost"
git config --global color.ui false

mkdir -p /src/work
cd /src/work

echo "=== repo init (twrp-9.0) ==="
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni -b twrp-9.0
echo "=== repo sync ==="
repo sync -j"$(nproc)" --force-sync --no-clone-bundle --no-tags

echo "=== place device tree ==="
mkdir -p device/xiaodu
rm -rf device/xiaodu/xps10e
cp -r /src/device/xiaodu/xps10e device/xiaodu/xps10e
ls -la device/xiaodu/xps10e

export ALLOW_MISSING_DEPENDENCIES=true
export LC_ALL=C
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"

echo "=== lunch ==="
set +u
source build/envsetup.sh
lunch omni_xps10e-eng
set -u

echo "=== build ==="
make -j"$(nproc)" recoveryimage

echo "=== result ==="
ls -la out/target/product/xps10e/recovery.img
sha256sum out/target/product/xps10e/recovery.img
