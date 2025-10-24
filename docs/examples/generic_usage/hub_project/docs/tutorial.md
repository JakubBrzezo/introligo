# Tutorial: Getting Started with MyProject

This tutorial will walk you through the basics of using MyProject.

## Step 1: Installation

First, install MyProject:

```bash
pip install myproject
```

## Step 2: Basic Usage

Create a simple script:

```python
from myproject import MyClass

# Create an instance
processor = MyClass(config={'mode': 'fast'})

# Process data
result = processor.process(data)
print(result)
```

## Step 3: Configuration

MyProject can be configured in multiple ways:

```python
# Option 1: Constructor arguments
processor = MyClass(mode='fast', debug=True)

# Option 2: Configuration file
processor = MyClass.from_config('config.yaml')

# Option 3: Environment variables
import os
os.environ['MYPROJECT_MODE'] = 'fast'
processor = MyClass()
```

## Step 4: Advanced Features

### Batch Processing

```python
# Process multiple items
results = processor.process_batch([item1, item2, item3])
```

### Async Support

```python
import asyncio

async def main():
    result = await processor.process_async(data)

asyncio.run(main())
```

## Next Steps

- Read the [User Guide](user-guide.md)
- Check the [API Reference](../api/index.html)
- See [Examples](examples.md)
