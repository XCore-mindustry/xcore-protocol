# Protocol Overview

## Purpose
Define the official communication model used between XCore components.

## Principles
- protocol-first
- language-neutral
- strict canonical contracts
- compatibility through explicit adapters
- stable route metadata

## Message Families
- moderation
- discord integration
- maps RPC
- chat and heartbeat

## Boundary
Application repositories consume this protocol. They do not independently redefine canonical wire contracts.
