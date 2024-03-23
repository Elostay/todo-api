#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1

uvicorn main:app --reload