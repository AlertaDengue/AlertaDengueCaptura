#!/bin/bash
exec celery worker -A crawlclima.fetchapp -l info --concurrency=4
