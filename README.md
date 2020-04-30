### SA2005 Control Panel

This is a Python-based GUI wrapper around the serial functionality of the BCBiomedical SA-2005. **NOTE:** Some functionality is not working as of this commit.

## Required Libraries:

* PyQt5

If you have Python3 installed with the PATH variables installed, you can run the command:

```
pip3 install PyQt5
```

to install PyQT. 

## Usage

The program will attempt to automatically detect the available COM ports from Windows. Plug the RS232 cable into the SA2005 and your computer. Then run 'main.pyw'.

If the libraries are installed, a GUI will open. At the bottom of the window, you can connect to the COM port associated with the SA2005. Once connected, you can operate the SA2005 through the GUI.

**IMPORTANT SAFETY WARNING:** The SA2005's physical ground disconnect button is momentary, meaning it will only disconnect ground while the button is held. With the serial and GUI interface, the ground disonnect is TOGGLED and will not reset automatically. This can present an electrocution hazard if the device under test (DUT) is faulty as the ground connection may be disconnected without it being obivous to the operator. There are no other protections in place to handle ground faults unless the SA2005 is connected to a GFCI.

Always verify the ground connection status before handling or operating the DUT.

