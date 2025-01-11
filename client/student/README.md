# Assignment Submission Tool

This tool helps you submit your assignments to the grading server. Follow these simple steps:

## For Each Assignment

1. Edit your name in `config.yaml`:
   - Open `config.yaml` in any text editor
   - Change `student_name: YOUR_NAME_HERE` to your actual name
   - Save the file

2. Write your code:
   - All your code should be in the `src/` directory
   - Don't modify the function names or signatures

3. Submit your assignment:
   ```bash
   python submit.py
   ```

## Troubleshooting

If you get any errors:
1. Make sure your name is set in `config.yaml`
2. Check that all your code is in the `src/` directory
3. Verify you have internet connection
4. Contact your professor if problems persist

## Files in this Package

- `submit.py` - The submission script
- `config.yaml` - Your configuration file
- `src/` - Directory containing the assignment template
- `README.md` - This help file 
