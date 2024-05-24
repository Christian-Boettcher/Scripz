# Scripz
**Simple python powered Flet(flutter) GUI for storing scripts or plain text entries in an organized fashion with single click copy to clipboard and Gemini API integration.**


# Download Here: 
[Releases](https://github.com/Christian-Boettcher/Scripz/releases/)

#

On first start you'll be greeted with a "Welcome" dialog
![FirstStart](https://github.com/Christian-Boettcher/Scripz/assets/103608972/1c254d13-8a95-4a4a-863a-357862454e5e)

#

Clicking the "Get started" button will open the Category Drawer, where you can click the "+" button to add a new category. (Hit [Enter] to submit the new category name)
![CategoryCreation](https://github.com/Christian-Boettcher/Scripz/assets/103608972/c0152f72-4d29-48cc-8ede-dd8c1c9da654)

#

# Category options:
![Category_Options](https://github.com/Christian-Boettcher/Scripz/assets/103608972/7604444f-cd5e-42d0-86ba-e085bba20779)


Clicking back in the main area you will now see the "+" Button on the right for adding new script entries.
![CreateScript](https://github.com/Christian-Boettcher/Scripz/assets/103608972/df9cc1e2-1678-4389-b6b7-04d834fd76df)

#

**Notice in the placeholder display how variables are set using {{}} eg: {{Username}}**
![ScriptCreation](https://github.com/Christian-Boettcher/Scripz/assets/103608972/1d2c1ffd-cc49-41ed-bfdf-da12be26c689)

#

# Demoing markdown syntax highlighting:
![SyntaxHighlighting](https://github.com/Christian-Boettcher/Scripz/assets/103608972/ff0b3529-8707-49a9-ac0f-a69cc1d0b355)

#

# Settings and version number display:
![Settings](https://github.com/Christian-Boettcher/Scripz/assets/103608972/9673e124-4606-4ab4-84da-b5f1ee3ab9b9)


#

# Enabling Gemini and adding API Key:
![Enabling_Gemini](https://github.com/Christian-Boettcher/Scripz/assets/103608972/be95569a-9419-4241-971e-b4979e268349)


With Gemini enabled and a working API Key you will see this generate button in NEW script creation window. 
Clicking this will automatically generate a script description based on what is in the script input field.
![Desciption_Generation](https://github.com/Christian-Boettcher/Scripz/assets/103608972/c26a5cb8-98ff-4a21-a9db-dce1d3e98a06)

#

# Other features:
## Searching in current category:
![Search](https://github.com/Christian-Boettcher/Scripz/assets/103608972/579eb2fc-81ac-45de-9353-5607f56ae949)

## Light/Dark Theme switching:
![LightMode](https://github.com/Christian-Boettcher/Scripz/assets/103608972/e966fa8a-5f09-432a-98d9-184588ef9605)


## Drag re-ordering:
![Drag_Handle](https://github.com/Christian-Boettcher/Scripz/assets/103608972/8cd18e39-b13a-4545-ae9b-e0113ab77608)



# TO-DO:
- [x] Add source code here
- [x] Fix "Generate" button not displaying after API Key added/Gemini Enabled.
      *(current workaraound is close and re-open after making changes)* <sub>whoops</sub>

- [ ] Find a way to verify script input is in fact "code" before generating description. *(currently Gemini will attempt to explain anything in script input field using 1-2 sentences)*
- [x] Flet currently has no way to limit minimum windows size. *(meaning the window can be resized so small it makes the UI look bad lol)* -Fixed with latest version
- [x] Searching does not clear/reset after desired result is found.
- [x] Minimizing has issues with restoring the window *(current workaround is closing and re-opening)* *will be pushing a patch on this soon*
- [x] Windows 11 minimize bug, minimizing in windows 11 causes the app to not be restored and has to close and re-open *looking into this more*
- [x] Re-ordering persistance
- [x] Add search hotkey?
- [ ] Add different color themes?
- [x] Add window title
