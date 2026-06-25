# Active Capacity Network (ACN)

> **Private preview / prototype.** Concept + working prototype only. No public
> mainnet, no live value.

## The idea

**Active Capacity Network (ACN)** is a protocol concept for **moving,
project-bound capacity**: network capacity that is allocated to approved projects,
moved, and whose activity is tracked and provable. The token unit is **ACAP**.

The differentiator is **activity**: capacity is valued when it is *in motion and in
use*, not merely held. This is captured by the consensus idea below.

## Proof of Active Capacity (PoAC)

**PoAC** selects participants by a blend of:

- **Stake / reserved capacity** — skin in the game.
- **Uptime** — the node is actually available.
- **Activity / movement** — capacity is being used, not idle.
- **Reputation** — consistent, honest participation over time.

There is **no Proof of Work** (no mining race, no energy-burn). PoAC is a design
stage model in this preview; the prototype demonstrates the data shapes, not a
production consensus guarantee.

## Roles (preview)

- **Validators / operators** — run nodes, participate in block production on a
  devnet/testnet.
- **Issuers / projects** — reserve active capacity for approved use cases.
- **Holders** — hold ACAP; capacity status depends on movement/participation
  (see [ACTIVE_CAPACITY_RESERVATION.md](ACTIVE_CAPACITY_RESERVATION.md)).

## First use case

The protocol is being demonstrated against a first project (the 469 Diamond
auction PoAC prototype). That project is the **first use case, not the whole
product**. Public-safe, read-only data from it is mirrored to show the protocol
"in motion" without any value moving.

## Relationship to this repo

This repo ships the **node**, **installer**, **devnet**, **tokenomics preview**,
and **docs** so anyone can inspect and run the prototype locally. The production
website and backend are intentionally **not** part of this public package.

## What ACN is not (yet)

No public mainnet, no custody, no bridge, no payments, no trading, no live
rewards. See [DISCLAIMERS.md](DISCLAIMERS.md).
