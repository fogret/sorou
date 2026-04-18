name: Channel AI to M3U

on:
  schedule:
    - cron: '0 0 * * *'  # 每天UTC0点运行
  workflow_dispatch:     # 允许手动运行

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install requests

      - name: Run channel_ai.py
        run: python channel_ai.py

      - name: Commit and push m3u
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          git add channels.m3u
          git commit -m "Auto update channels.m3u"
          git push
