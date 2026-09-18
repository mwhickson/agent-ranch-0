# TinyCP Library

## Overview

TinyCP Library is a library intended to serve as a backbone for the upcoming Tiny Computer People (TinyCP) game.

This library will establish the game logic core, and should be flexible, modular and performant to enable it to operate under the high performance requirements imposed by serving as the "heart" of a game loop.

TinyCP is intended to be a life sim, similar to projects like `Little Computer People` or `The Sims`, though it's scope is much simpler than either game.

The library MUST allow for the following:

- modeling a Tiny Computer Person using attributes
- tracking the passage of time in abstract units (`TimeUnits`)
- applying attribute changes over time

### Defining a Tiny Computer Person

A Tiny Computer Person can be defined by the following attributes:
- Name
- Overall Status
- Metrics
- Location
- Activity

### Overall Status

Overall status is determined by evaluating the current state of the Metric values recorded for a Tiny Computer Person.

Allowable values (in descending order of desirability) are:
- Content (most desirable) - 3 of 5 metrics in Good Status; 0 metrics in Bad Status
- Comfortable - 0 metrics in Bad Status
- Neutral - Default state, covers any Status not otherwise covered
- Uncomfortable - 0 metrics in Good Status
- Miserable (least desirable) - 3 of 5 metrics in Bad Status; 0 metrics in Good Status

> NOTE: Good Status and Bad Status are detailed below in the Metrics List table.

### Metrics List

Metrics are rated on a scale from 0 to 255 and change over time.

Managing Metrics defining the state of a Tiny Computer Person are:

| Name | Minimum Value | Maximum Value | Default Value | Desired Value | Good Status | Bad Status |
| - | - | - | - | - | - | - |
| Energy | 0 | 255 | 255 | 255 | >= 200 | <= 100 |
| Happiness | 0 | 255 | 255 | 255 | >= 200 | <= 100 |
| Hunger | 0 | 255 | 0 | 0 | <= 100 | >= 200 |
| Hygiene | 0 | 255 | 255 | 255 | >= 200 | <= 100 |
| Thirst | 0 | 255 | 0 | 0 | <= 100 | >= 200 |

- All metric updates must be clamped to [0, 255] after every TimeUnit calculation.
- Hunger and Thirst are inverted metrics where 0 is ideal. Lower values represent Good Status and higher values represent Bad Status.

### Locations List

Locations available for a Tiny Computer Person to inhabit are:

- Bathroom
- Bedroom
- Kitchen
- Living Room
- Office

### Activities List

Activities a Tiny Computer Person may undertake include:

| Name | Purpose | Required Location | Energy Change | Happiness Change | Hunger Change | Hygiene Change | Thirst Change |
| - | - | - | - | - | - | - | - |
| Cleaning (themselves) | Improve Hygiene Score | Bathroom | -5 | (0, 5) | 0 | (5, 10, 15, 20) | 0 |
| Doing Nothing | Default State | Any | (-5, 0) | (-5, 0, 5) | (-5, 0) | 0 | (-5, 0) |
| Drinking | Improve Thirst Score | Kitchen | -5 | (0, 5, 10) | (-5, 0, 5) | (-5, 0, 5) | (-15, -10, -5) |
| Eating | Improve Hunger Score | Kitchen | -5 | (0, 5, 10) | (-15, -10, -5) | (-10, -5, 0) | (-5, 0, 5) |
| Housework | Improve Hygiene Score | Any | (-20, -10, -5) | (0, 5, 10) | (0, 5) | (5, 10, 20) | (0, 5) |
| Listening to Music | Improve Happiness Score | Living Room | -5 | (0, 5, 10) | 0 | 0 | 0 |
| Playing a Game | Improve Happiness Score | Living Room | (-5, 5) | (-15, -10, -5), (0, 5, 10, 15) | (0, 5) | (-5, 0) | (0, 5) |
| Reading a Book | Improve Happiness Score | Living Room | -5 | (0, 5, 10) | (0, 5) | 0 | (0, 5) |
| Sleeping | Improve Energy Score | Bedroom | (-5, 0, 10, 20, 30) | (-5, 0, 5) | (5, 10) | (-10, -5, 0) | (5, 10) |
| Thinking | Select Next Activity | Any | (-10, -5, 0, 5, 10) | (-5, 0, 5) | (0, 5) | 0 | (0, 5) |
| Watching Videos | Improve Happiness Score | Living Room | -5 | (-10, -5, 5, 10) | (0, 5) | 0 | (0, 5) |
| Working | Improve or Lower Happiness Score | Office | (-30, -15, -5) | (-15, -10, -5, 0, 5, 10, 15) | (0, 5, 10) | (-10, -5, 0) | (0, 5, 10) |

- All changes listed above are per TimeUnit.
- Some Metric changes are variable, and a value should be randomly determined when applying.
- Tuples of values represent discrete choice sets (e.g. pick randomly from [-15, -10, -5]), not continuous range bounds.
- Activity effects are only applied at the completion of a TimeUnit. Fractional/decimal effects are NOT to be supported.

## Time Tracking in Game

Time is tracked in this library for the game engine in abstract units called `TimeUnits` (singular `TimeUnit` - e.g. 1 TimeUnit, 2 TimeUnits, 100 TimeUnits).

TimeUnits has been selected to differentiate from other common terms (such as `Ticks`) to avoid confusion with game library or operating system time unit abstractions.

A TimeUnit is intended to be standardized, but may represent a block of time like 10 minutes, 1 hour or 1 day.

Fractional/decimal values should be permitted when calculating elapsed time.

## Configuration
<!-- AR0_CONFIG: API_URL=http://localhost:5001/v1/chat/completions -->

---

## Technical Stack

### Approved
* **Languages & Runtimes:** Python, Bash

### Prohibited
* **Remote Network Access:** Strictly forbidden by default. Remote resources may only be accessed via local network bridges explicitly authorized by the Human Orchestrator.

---

## Execution Guidelines

1. **Output Standard:** Prioritize human-readable, human-verifiable, and machine-reproducible artifacts over dense black-box outputs.
