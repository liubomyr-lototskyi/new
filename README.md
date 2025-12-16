## 🌟 File Integrity Checker uses SHA-256 cryptographic hashing to create a baseline of your critical files and detect any changes.

### Detect unauthorized modifications to system files, configurations, or sensitive documents
### Meet audit requirements for file integrity monitoring (FIM)</h3>
### Early warning system for file encryption attacks</h3>
### Track and verify intentional vs. unintentional file changes</h3>

> First, create a test file to monitor
```py
echo "Hello World" > test.txt
```

> Add it to monitoring
```py
python file_integrity_checker.py add test.txt
```

> Check integrity (should show all intact)
```py
python file_integrity_checker.py check
```

> Now modify the test file
```py
echo "Modified content" > test.txt
```

> Check again (should detect the modification!)
```py
python file_integrity_checker.py check
```

> List all monitored files
```py
python file_integrity_checker.py list
```
