# Installation

Installing ZacrosTools is straightforward. Follow the steps below to get started with the library, whether you prefer using `pip` for a quick setup or cloning the repository for development purposes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation via pip](#installation-via-pip)
- [Installing from Source](#installing-from-source)

## Prerequisites

Before installing ZacrosTools, ensure that you have the following installed on your system:

- **Python 3.8 or higher**: ZacrosTools is compatible with Python versions 3.8 and above.
- **pip**: Python's package installer. It usually comes bundled with Python installations.

## Installation via pip

The easiest and quickest way to install ZacrosTools is using `pip`. This method is suitable for most users who want to use the library without modifying the source code.

1. **Open your terminal or command prompt.**

2. **Run the following command:**

    ```bash
    pip install zacrostools
    ```

3. **Verify the installation:**

    After the installation completes, you can verify it by importing ZacrosTools in Python:

    ```python
    import zacrostools
    print(zacrostools.__version__)
    ```

    This should display the installed version of ZacrosTools without any errors.

## Installing from Source

If you want to contribute to ZacrosTools or use the latest development version, you can install it directly from the GitHub repository.

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/hprats/ZacrosTools.git
    ```

2. **Navigate to the Project Directory:**

    ```bash
    cd ZacrosTools
    ```

3. **Install the Package:**

    ```bash
    pip install .
    ```

    This command installs ZacrosTools in your Python environment.

4. **Verify the Installation:**

    Similar to the `pip` installation, verify by importing the library:

    ```python
    import zacrostools
    print(zacrostools.__version__)
    ```

### **Installing Development Dependencies**

If you plan to contribute to ZacrosTools or run the test suite locally, you may need additional dependencies like `pytest`.

1. **Install pytest:**

    ```bash
    pip install pytest
    ```

2. **Run Tests:**

    ```bash
    pytest
    ```
