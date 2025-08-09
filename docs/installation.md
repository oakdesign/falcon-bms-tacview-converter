# Installation Instructions for Falcon BMS Tacview Airbase Converter

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.6 or higher
- pip (Python package installer)

## Installation Steps

1. **Clone the Repository**

   Open your terminal and run the following command to clone the repository:

   ```
   git clone https://github.com/yourusername/falcon-bms-tacview-converter.git
   ```

   Replace `yourusername` with your GitHub username.

2. **Navigate to the Project Directory**

   Change into the project directory:

   ```
   cd falcon-bms-tacview-converter
   ```

3. **Install Required Dependencies**

   Use pip to install the necessary dependencies listed in `requirements.txt`:

   ```
   pip install -r requirements.txt
   ```

4. **Configure the Project**

   Edit the `src/config.py` file to set your Falcon BMS installation path and adjust any theater configurations as needed.

5. **Run the Converter**

   You can now run the converter using the command line. For example, to use the default theater (Korea):

   ```
   python src/eval_airbases_to_tacview_final.py
   ```

## Troubleshooting

If you encounter any issues during installation, please refer to the troubleshooting section in the `README.md` file for guidance.