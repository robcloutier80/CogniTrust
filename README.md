# CogniTrust v2.3

CogniTrust v2.3 is an open-source AI trust evaluation system designed to provide **confidence scores** for statements using multiple open-source backends.

## Key Features
- **Multi-backend confidence scoring**: DuckDuckGo, Haystack, LLaMA2, MPT, GPT4All
- **Equal weighting** for all sources
- **Color-coded console output** with symbols: ✅ ⚠️ ❗ 🛑
- **Handles partial scores and API failures gracefully**
- **Caching per session**, persisted to local JSON file (user-clearable)
- **Interactive console demo** (`demo.py`)
- **Plugin hooks** for optional paid or proprietary backends

## Requirements
- Python 3.8+
- `requests` library (install via `pip install requests`)

## Usage
```bash
git clone <repo-url>
cd CogniTrust
python demo.py