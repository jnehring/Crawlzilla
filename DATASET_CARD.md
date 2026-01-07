# Dataset Card for Crawlzilla Corpus

## Dataset Description

### Dataset Summary

The Crawlzilla Corpus is a collection of web-crawled text data for training Large Language Models (LLMs) on 8 African languages. The dataset is generated using the [Crawlzilla](https://github.com/jnehring/crawlzilla) web crawler by the Mbaza community. This dataset aims to:

- **Democratize AI**: Enable LLM development for underrepresented African languages
- **Preserve Languages**: Create digital resources for languages with limited online presence
- **Support Research**: Provide training data for NLP research in low-resource settings

The first published outcome of this project is the [Mbaza Monolingual Corpus 1.1](https://huggingface.co/datasets/mbazaNLP/kinyarwanda_monolingual_v01.1). This dataset is the extended version.

### Supported Languages

The dataset supports multiple African languages, identified using ISO 639-3 language codes and ISO 15924 script codes:

| Language    | ISO 639-3 Code   | Script (ISO 15924 Code)   |   Num words [Mio] |   Num characters [Mio] |   Num sentences [Mio] |
|:------------|:-----------------|:--------------------------|------------------:|-----------------------:|----------------------:|
| Afrikaans   | afr              | Latn                      |           94.3124 |                557.347 |               5.78757 |
| Hausa       | hau              | Latn                      |          106.532  |                598.035 |               4.99128 |
| Swahili     | swh              | Latn                      |          123.031  |                786.161 |               6.87675 |
| Amharic     | amh              | Ethi                      |           88.4559 |                455.751 |               3.56739 |
| Somali      | som              | Latn                      |          128.155  |                842.004 |               6.31182 |
| Xhosa       | xho              | Latn                      |           39.1105 |                351.979 |               3.08705 |
| Yoruba      | yor              | Latn                      |           45.549  |                253.041 |               1.68044 |
| Kinyarwanda | kin              | Latn                      |           53.0348 |                388.808 |               2.84802 |
| Total       | -                | -                         |          678.182  |               4233.13  |              35.1503  |

### Dataset Structure

#### Data Fields

The final dataset is stored in Apache Parquet format with the following schema:

| Field      | Type          | Description                                      |
|------------|---------------|--------------------------------------------------|
| `text`     | large_string  | The extracted and cleaned text content           |
| `language` | dictionary    | ISO 639-3 language code (e.g., "kin", "swa")     |
| `script`   | dictionary    | ISO 15924 script code (e.g., "Latn", "Ethi")     |

#### Data Splits

The dataset is provided as a single training split, with data organized by language.

---

## Dataset Creation

The data was crawled from public sources using the [Crawlzilla](https://github.com/jnehring/crawlzilla) software. Crawlzilla implements several ethical crawling measures:

- **robots.txt Compliance**: Respects website crawling rules via `robots.txt` parsing
- **Meta Robots Tags**: Honors `noindex` and `nofollow` directives in HTML meta tags
- **Crawl Delay**: Implements configurable delays between requests (default: 1 second)
- **Rate Limiting**: Never downloads multiple pages from the same domain simultaneously
- **User-Agent Identification**: Identifies itself as `Crawlzilla/1.0`
