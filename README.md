<h1>File Integrity Checker uses SHA-256 cryptographic hashing to create a baseline of your critical files and detect any changes. </h1>

Detect unauthorized modifications to system files, configurations, or sensitive documents
Meet audit requirements for file integrity monitoring (FIM)
Early warning system for file encryption attacks
Track and verify intentional vs. unintentional file changes

& First, create a test file to monitor
echo "Hello World" > test.txt

& Add it to monitoring
python file_integrity_checker.py add test.txt

& Check integrity (should show all intact)
python file_integrity_checker.py check

& Now modify the test file
echo "Modified content" > test.txt

& Check again (should detect the modification!)
python file_integrity_checker.py check

& List all monitored files
python file_integrity_checker.py list
