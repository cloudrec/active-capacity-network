# Active Capacity Reservation

> **Preview model.** Reservation is **disabled** (`reservation_active=false`,
> `available_for_reservation=0`). This describes the design, not a live offer, and
> is not investment advice.

## Not a fixed-term lease

The Active Capacity Reservation model is deliberately **not** a fixed-term lease:

- **ACAP belongs to the holder.** There is no fixed expiration term.
- You reserve **active network capacity** — you are not renting tokens for a period.
- ACAP remains yours while held; **nothing expires or is confiscated** after a term.

## Active vs inactive capacity

- **Active-capacity status** depends on **movement, node use, reservation activity,
  or other network participation**.
- **Inactive ACAP is not confiscated.** Its active-capacity *weight* may pause,
  decay, or become inactive until reactivated.
- **Reactivation** happens through movement, node participation, or other defined
  network actions.

## Where value is meant to come from

From **capacity, movement, participation, anti-spam, and network usefulness** —
**not** from a rental clock and **not** from a profit promise.

## Pricing as a capacity mechanism

When/if a reservation pool opens, tiered pricing means later reservations cost
more as the active-capacity pool fills. This is a **capacity-pricing mechanism** to
allocate scarce capacity — it is not a yield, dividend, or investment return.

## Current state

- `reservation_active`: **false**
- `available_for_reservation`: **0**
- Pool 1: **planned, not open** (`available_now=0`).

Any future change requires legal and contract review and will be versioned in the
changelog. See [DISCLAIMERS.md](DISCLAIMERS.md).
