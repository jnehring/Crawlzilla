# Dataset Card for Crawlzilla Monolingual Corpus

## Dataset Description

### Dataset Summary

The Crawlzilla Monolingual Corpus is a collection of web-crawled text data specifically designed for training Large Language Models (LLMs) on low-resource African languages. The dataset is generated using the [Crawlzilla](https://github.com/jnehring/crawlzilla) web crawler, which implements ethical and friendly crawling practices.

The first published outcome of this project is the [Mbaza Monolingual Corpus 1.1](https://huggingface.co/datasets/mbazaNLP/kinyarwanda_monolingual_v01.1).

### Supported Languages

The dataset supports multiple African languages, identified using ISO 639-3 language codes and ISO 15924 script codes:

| Language    | ISO 639-3 Code | Script (ISO 15924) | Combined Code |
|-------------|----------------|-------------------|---------------|
| Kinyarwanda | kin            | Latin             | kin_Latn      |
| Kirundi     | run            | Latin             | run_Latn      |
| Swahili     | swa            | Latin             | swa_Latn      |
| Hausa       | hau            | Latin             | hau_Latn      |
| Amharic     | amh            | Ge'ez (Ethiopic)  | amh_Ethi      |
| Yoruba      | yor            | Latin             | yor_Latn      |
| Oromo       | orm            | Latin             | orm_Latn      |
| Lingala     | lin            | Latin             | lin_Latn      |

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

### Source Data

#### Initial Data Collection

Seed URLs are collected from [CommonCrawl](https://commoncrawl.org/) using Amazon Athena queries. The process involves:

1. **Querying CommonCrawl**: URLs are extracted based on language detection metadata
2. **Deduplication**: Duplicate URLs are removed at the domain level
3. **Script Assignment**: Each language is assigned its appropriate script (Latin for most African languages, Ge'ez for Amharic)

Example Athena query used:
```sql
SELECT url, url_host_registered_domain, content_languages
FROM "ccindex"."ccindex"
WHERE subset = 'warc' AND content_languages IN ('swa', 'hau', 'amh', 'yor', 'orm', 'kin', 'rin');
```

### Data Collection Methodology

The Crawlzilla crawler operates in a round-based approach:

```
┌─────────────────┐
│   Seed URLs     │ ──► Initial URLs from CommonCrawl
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  URLs2Download  │ ──► Queue of URLs to be crawled
└────────┬────────┘
         │
    ┌────┴────┐
    │  Round  │ ◄─────────────────────────────────┐
    └────┬────┘                                   │
         │                                        │
         ▼                                        │
┌─────────────────┐                               │
│     Fetch       │ ──► Download HTML content     │
└────────┬────────┘                               │
         │                                        │
         ▼                                        │
┌─────────────────┐                               │
│     Parse       │ ──► Extract text & links      │
└────────┬────────┘                               │
         │                                        │
         ├──► Text ──► Language Detection         │
         │              (FastText)                │
         │                                        │
         └──► Links ──► Filter & Add to Queue ────┘
```

#### Crawling Process

1. **Round-based Crawling**: Each round downloads a configurable number of URLs (default: 1000)
2. **Batch Processing**: URLs are batched for parallel download (default batch size: 250)
3. **Domain Diversity**: Each batch contains at most one URL per domain to ensure friendly crawling
4. **Parallel Execution**: Multi-threaded downloading (default: 10-50 threads)

#### Ethical Crawling Practices

Crawlzilla implements several ethical crawling measures:

- **robots.txt Compliance**: Respects website crawling rules via `robots.txt` parsing
- **Meta Robots Tags**: Honors `noindex` and `nofollow` directives in HTML meta tags
- **Crawl Delay**: Implements configurable delays between requests (default: 1 second)
- **Rate Limiting**: Never downloads multiple pages from the same domain simultaneously
- **User-Agent Identification**: Identifies itself as `Crawlzilla/1.0`

### Text Extraction and Processing

#### HTML to Text Conversion

The `HTML2Text` class extracts clean text from HTML documents:

1. **Node Selection**: Extracts text from semantic HTML elements (`<p>`, `<span>`, `<h1>`-`<h6>`)
2. **Quality Filtering**: Applies multiple heuristics to ensure text quality:
   - **Minimum Length**: Text segments must be at least 50 characters
   - **Sentence Markers**: Must contain punctuation (`.`, `,`, `!`, `?`)
   - **Case Ratio**: Filters out text with abnormal upper/lowercase ratios
   - **Truncation Detection**: Excludes text ending with `...`
3. **Whitespace Normalization**: Consecutive whitespace is collapsed

#### Language Identification

Language detection is performed using [FastText's language identification model](https://huggingface.co/facebook/fasttext-language-identification):

- Each text segment is classified independently
- Documents must have ≥80% of content in the target language(s) to be included
- Only segments matching the target language are retained

### Data Cleaning and Deduplication

#### Sentence-Level Deduplication

The `generate_dataset.py` script performs hash-based deduplication:

```python
dedups = set()
for line in file:
    h = hash(line)
    if h in dedups:
        continue
    dedups.add(h)
    # ... process line
```

#### Quality Criteria

Text is considered "good clean text" if it:
- Contains complete sentences with proper grammar
- Is not a navigation fragment (e.g., "Home", "News", "Sport")
- Is not a timestamp or metadata (e.g., "8 hours ago")
- Is not a call-to-action fragment (e.g., "Follow BBC on:")

---

## Dataset Statistics

Statistics are computed during dataset generation and include:

| Metric      | Description                                    |
|-------------|------------------------------------------------|
| words       | Total word count (space-separated tokens)      |
| characters  | Total character count                          |
| sentences   | Sentence count (via NLTK tokenization)         |

Statistics are saved to `stats.csv` in the output folder.

---

## Output Formats

### Primary Format: Parquet

The final dataset is stored in Apache Parquet format with:
- **Compression**: ZSTD compression for efficient storage
- **Dictionary Encoding**: Language and script fields use dictionary encoding
- **Batch Size**: Default 500,000 samples per file (~40MB per batch)

### Alternative Format: WARC

Crawlzilla can optionally output data in [WARC (Web ARChive)](https://en.wikipedia.org/wiki/Web_ARChive) format, compatible with tools like the [OSCAR project](https://oscar-project.org/).

---

## Considerations for Using the Data

### Social Impact

This dataset aims to:
- **Democratize AI**: Enable LLM development for underrepresented African languages
- **Preserve Languages**: Create digital resources for languages with limited online presence
- **Support Research**: Provide training data for NLP research in low-resource settings

### Limitations

- **Web Bias**: Data reflects the content available on the web, which may not represent all language varieties or registers
- **Quality Variance**: Despite filtering, some noise may remain in the data
- **Temporal Snapshot**: Data represents a point-in-time snapshot of web content
- **Domain Distribution**: Certain domains or topics may be overrepresented

### Ethical Considerations

- **Copyright**: Web-crawled data may include copyrighted content; users should consider fair use implications
- **Privacy**: While the crawler respects robots.txt, some personal information may be present
- **Bias**: Web content may contain biases that could be learned by models trained on this data

---

## Technical Requirements

### Software Dependencies

```
beautifulsoup4==4.13.3
fasttext==0.9.3
huggingface_hub==0.29.2
nltk==3.9.1
numpy==1.22.0
warcio==1.7.5
pandas==2.0.3
pyarrow==17.0.0
flask==3.1.2
```

### Hardware Requirements

- **Minimal Setup**: Can run on a single laptop
- **No Infrastructure**: Does not require databases or server infrastructure
- **Storage**: Depends on crawl size; intermediate files can be deleted to save space

---

## Citation

If you use this dataset, please cite:

```bibtex
@software{crawlzilla2025,
  title = {Crawlzilla: A Web Crawler for Low-Resource Language LLM Training Data},
  author = {Crawlzilla Team},
  year = {2025},
  url = {https://github.com/jnehring/crawlzilla},
  license = {MIT}
}
```

---

## License

The Crawlzilla software is released under the [MIT License](LICENSE).

**Note**: The license applies to the crawler software. The crawled data may be subject to the original content's copyright and terms of use.

---

## Additional Resources

- [GitHub Repository](https://github.com/jnehring/crawlzilla)
- [How to Generate Seed URLs from CommonCrawl](doc/create_seed_urls.ipynb)
- [What is Good Clean Text for Language Models](doc/what-is-good-clean-test.md)
- [Generate Dataset Documentation](doc/generate-dataset.md)
- [Mbaza Monolingual Corpus 1.1](https://huggingface.co/datasets/mbazaNLP/kinyarwanda_monolingual_v01.1)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0     | 2025 | Initial release |

---

## Contact

For questions or issues, please open an issue on the [GitHub repository](https://github.com/jnehring/crawlzilla/issues).
