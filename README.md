# ANPR Detection Validator Pro

A professional desktop application for validating Automatic Number Plate Recognition (ANPR) detection results. Built with Python and Tkinter, this tool streamlines the process of reviewing and validating license plate detection accuracy.

## Features

### Core Functionality
- **CSV Data Loading**: Import detection results with support for required columns (vdata_id, fr_anpr, re_anpr, fr_mediaid, re_mediaid)
- **Dual Image Viewer**: Side-by-side display of front and rear vehicle images
- **Advanced Zoom System**: Click-to-zoom functionality with original resolution viewing
- **Validation Workflow**: Mark detections as correct or categorize errors
- **Progress Tracking**: Real-time validation statistics and progress bar
- **Export Results**: Generate validated CSV files with validation status

### Image Viewing
- **In-place Zoom**: Click on any area to zoom with preserved image quality
- **Pan & Navigate**: Drag to move around zoomed images
- **Mouse Wheel Support**: Smooth zoom in/out with scroll wheel
- **Multiple Format Support**: JPG, PNG, BMP, TIFF image formats
- **Smart File Matching**: Flexible filename matching with multiple extensions

### Validation System
- **Quick Validation**: One-click correct/wrong marking
- **Error Categorization**: Detailed error types including:
  - Hidden/Broken plates
  - Blur issues
  - No license plate
  - No vehicle
  - Motorcycles
  - Wrong vehicle pairing
- **Auto-advance**: Automatically move to next record after validation
- **CSV Export**: Creates validated CSV files with validation results

### User Experience
- **Keyboard Shortcuts**: Arrow keys for navigation, ESC to close popups
- **Modern UI**: Professional interface with progress indicators
- **Status Updates**: Real-time feedback on validation progress
- **Error Handling**: Robust file loading with helpful error messages

## Installation

### Prerequisites
- Python 3.7 or higher
- Required packages (install via pip):

```bash
pip install pandas pillow
```

### Quick Start
1. Clone this repository:
```bash
git clone https://github.com/Yousef-Alhattab/ANPR-Detection-Validator-Pro.git
cd ANPR-Detection-Validator-Pro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python anpr_validator.py
```

## Usage

### Getting Started
1. **Load CSV File**: Click "Browse CSV" to select your detection results file
2. **Set Image Path**: Click "Browse Folder" to select the directory containing your images
3. **Start Validation**: Navigate through records using Previous/Next buttons

### CSV Format Requirements
Your CSV file must contain these columns:
- `vdata_id`: Unique identifier for each record
- `fr_anpr`: Front plate detection result
- `re_anpr`: Rear plate detection result  
- `fr_mediaid`: Front image filename
- `re_mediaid`: Rear image filename

### Validation Workflow
1. **Review Detection**: Check if the displayed detection matches the actual plate
2. **Mark Result**: Click Correct or Wrong for each plate
3. **Error Details**: If wrong, select specific error type from the popup
4. **Auto-advance**: System moves to next record automatically when both plates are validated

### Keyboard Shortcuts
- **Arrow Keys**: Navigate between records
- **ESC**: Close popup windows or clear focus
- **Mouse Wheel**: Zoom in/out on images
- **+/-**: Zoom in/out in popup windows
- **R**: Reset zoom to original size

## Output Files

The application generates:
- **Validated CSV**: Main output with validation results
- **Columns added**: fr_validation, re_validation
- **Values**: "correct" or specific error codes (e.g., "blur", "hidden", "no_LP")

## File Structure
```
ANPR-Detection-Validator-Pro/
├── anpr_validator.py          # Main application file
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── screenshots/              # Application screenshots
├── examples/                 # Sample CSV files
└── docs/                    # Additional documentation
```

## Technical Details

### Architecture
- **GUI Framework**: Tkinter with custom styling
- **Image Processing**: PIL (Python Imaging Library)
- **Data Handling**: Pandas for CSV operations
- **Resolution**: Maintains original image quality during zoom operations

### Performance Features
- Lazy image loading for large datasets
- Efficient memory management for image display
- Fast validation workflow with minimal clicks
- Optimized file matching algorithms

### Error Handling
- Robust CSV validation with clear error messages
- Flexible image file matching (multiple extensions, path variations)
- Graceful handling of missing files
- User-friendly error notifications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/Yousef-Alhattab/ANPR-Detection-Validator-Pro/issues) page
2. Create a new issue with detailed information about your problem
3. Include sample data and error messages when possible

## Changelog

### v1.0.0 (Current)
- Initial release with full validation workflow
- Advanced zoom and pan functionality
- CSV export with validation results
- Professional UI with progress tracking
- Comprehensive error categorization system

## Roadmap

- [ ] Batch processing mode
- [ ] Custom validation rules
- [ ] Database integration
- [ ] Multi-language support
- [ ] Advanced reporting features
- [ ] API integration for automated workflows

---

**Built with Python & Tkinter** | **Professional ANPR Validation Tool**
