# Text Summarization and Test Generation Client

A client script for generating structured XML summaries and tests using DeepSeek AI through the FastAPI server.

## Features

- Generates structured XML summaries of text
- Creates tests with multiple-choice questions based on summaries
- Extracts content in standardized XML formats
- Supports input from both files and standard input
- Saves the generated content to files

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)
- Running FastAPI server with DeepSeek AI integration

## Usage

### Basic Usage

```bash
python client.py
```

This will prompt you to choose whether you want to generate a summary or a test, then guide you through the process.

### Command Line Options

```bash
python client.py [--file FILE] [--token TOKEN] [--server SERVER] [--questions NUM]
```

Options:
- `--file`: Path to a text file to summarize
- `--token`: Your DeepSeek API token
- `--server`: Server URL (default: http://localhost:8000)
- `--questions`: Number of questions for test generation (default: 5)

## Workflow

1. **Summary Generation**: The script can generate a structured XML summary from text
2. **Test Generation**: The script can generate a test with multiple-choice questions from a summary
3. **Integrated Flow**: You can generate a summary and then immediately create a test from it

## Output Formats

### Summary Format

```xml
<summary>
    <summary_piece>
        <subtitle>
            Subtitle
        </subtitle>
        <text>
            Summary text
        </text>
    </summary_piece>
    <!-- Additional summary pieces -->
</summary>
```

### Test Format

```xml
<test>
    <question>
        <text>Question text</text>
        <answer>
            <text>Answer text</text>
            <is_correct>true/false</is_correct>
        </answer>
        <answer>
            <text>Answer text</text>
            <is_correct>true/false</is_correct>
        </answer>
        <answer>
            <text>Answer text</text>
            <is_correct>true/false</is_correct>
        </answer>
        <answer>
            <text>Answer text</text>
            <is_correct>true/false</is_correct>
        </answer>
    </question>
    <!-- Additional questions -->
</test>
```

## Output Files

- **Summary**: Saved to `summary_output.xml` in the current directory
- **Test**: Saved to `test_output.xml` in the current directory

## Examples

### Generate a Summary

```bash
python client.py --file example_text.txt
# When prompted, enter "summary"
```

### Generate a Test with 10 Questions

```bash
python client.py --questions 10
# When prompted, enter "test"
```

### Generate a Summary and then a Test

```bash
python client.py
# When prompted, enter "summary"
# When asked if you want to generate a test, enter "yes"
``` 