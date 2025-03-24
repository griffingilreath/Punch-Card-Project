# Bug: LED Test File Not Found in Expected Location

## Bug Description
The `test_leds.py` file referenced in the README documentation cannot be found in the expected location.

## Reproduction Steps
1. Attempt to run the test script as documented in the README:
```bash
cd /Users/griffingilreath/Documents/Coding/Cursor/Punch\ Card\ Project/ && python3 tests/test_leds.py --test animations --use-ui --char-set circle
```
2. Observe the error message:
```
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3: can't open file '/Users/griffingilreath/Documents/Coding/Cursor/Punch Card Project/tests/test_leds.py': [Errno 2] No such file or directory
```

## Expected Behavior
The test script should be located at the path specified in the README documentation and should run successfully.

## Potential Causes
- The test file may have been moved during project reorganization
- The README may not have been updated to reflect the new file location
- The test file may be missing altogether

## Proposed Solution
1. Locate the current position of the test file:
```bash
find /Users/griffingilreath/Documents/Coding/Cursor/Punch\ Card\ Project/ -name "test_leds.py"
```
2. Either:
   - Move the file to the correct location, or
   - Update the README to reflect the actual location, or
   - Recreate the test file if it's missing

## Priority
Low

## Labels
bug, documentation, testing 