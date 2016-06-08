# Spiders.py

This is a simple Python script from a code interview question that sequentially queries Books.com.tw, Momohome, PCHome
and Yahoo with a search query, and then prints out any search results found. The search results are not formatted or
sorted in any way. Pagination is on a best effort basis.

## Usage

    python spiders.py <search query>

## Requirements

    beautifulsoup4>=4.0
    requests>=2.8.1

## Known Issues

- Momoshop pagination is not supported.
- For most sites we do not display results for pages past the 10th page.
