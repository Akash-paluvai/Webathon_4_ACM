#!/bin/bash
set -e

# Verify Motoko compiler
if [ ! -x "/home/ubuntu/.motoko/moc/0.16.3-implicits-26/bin/moc" ]; then
    echo "Error: Motoko compiler not found at /home/ubuntu/.motoko/moc/0.16.3-implicits-26/bin/moc" >&2
    exit 1
fi

if [ ! -d "/home/ubuntu/.motoko/core/implicits-20" ]; then
    echo "Error: Motoko core library not found at /home/ubuntu/.motoko/core/implicits-20" >&2
    exit 1
fi

# Install dependencies
pnpm install --frozen-lockfile --prefer-offline --child-concurrency 2 --network-concurrency 6

# Build frontend
pnpm --filter '@caffeine/template-frontend' build:skip-bindings

# Optimize images
node scripts/prune-unused-images.js
node scripts/resize-images.js

# Build backend (compile Motoko to WASM)
/home/ubuntu/.motoko/moc/0.16.3-implicits-26/bin/moc \
    --implicit-package core \
    --default-persistent-actors \
    -no-check-ir \
    -E M0236 -E M0235 -E M0223 -E M0237 \
    --actor-idl backend/system-idl \
    --package core /home/ubuntu/.motoko/core/implicits-20 \
    backend/main.mo \
    -o backend/backend.wasm