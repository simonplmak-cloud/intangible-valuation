name: Bug Report
description: Report a bug or unexpected behavior
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to report a bug. Please fill in the information below.
  - type: input
    id: version
    attributes:
      label: Library Version
      description: What version of intangible-valuation are you using?
      placeholder: "e.g., 1.0.0"
    validations:
      required: true
  - type: input
    id: python-version
    attributes:
      label: Python Version
      description: What Python version are you using?
      placeholder: "e.g., 3.11.5"
    validations:
      required: true
  - type: input
    id: os
    attributes:
      label: Operating System
      description: What OS are you using?
      placeholder: "e.g., Ubuntu 22.04, macOS 14.0, Windows 11"
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: Description
      description: A clear and concise description of the bug.
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Minimal code example that reproduces the issue.
      render: python
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened? Include full error traceback if applicable.
    validations:
      required: true
