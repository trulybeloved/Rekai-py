
# TO DO

## Rekai
High Priority:
- Create a system to store config files/prepare a dedicated db for config and avoid hard coded values.
- Refactor to improve readability and organization
- Better API handling - Implement cryptographically hashed API keys stored in Local DB with Private Key in user folder. (Fernet)
- Webscraping is presently super slow. Needs optimization or replacement with a function equivalent to Jisho Sentence Parsing
  - Replace Selelium with pypeteer or playwrite-python, which supports async
- Need to implement Backoff/retry for transmutors

- WEBGUI
    - Complete webgui frontend design
    - Implement Options and settings to the backend. Right now only the frontend code is implemented
    - Expose AppConfig to frontend

Low Priority:
- Implement cutlet for romanization
- Pattern and pronoun tagging for dialogues.
- Enable TL of Paragraphs Directly

Eventually
- Other forms of output, like Markdown or Plaintext
- Better Databases


- ~~Implement preprocessing function. Bikatr6/Kudasai/Kairyou can be refactored and incorporated.~~
- ~~Implement clause by clause analysis - Clause class, splitting function~~
  - ~~Clause wise TTS and copy buttons~~
  - ~~Clause wise translations~~
- ~~Implement DeepL TL via API~~

## Rekai_HTML

- ~~Make the Omnibar actually omni - Direct MoS integration, embedded chapter search, with tabs to select between.??~~
- Implement a reader mode. TLs to be dynamically generated using JS for all paragraphs
- Incorporate adjustable fonts and colors
- Tooltips for buttons
- Controls and functionality for changing TTS playback rate 
- Chapter Search iframe
- Click to send to chapter search feature

- ~~Making the natural appearance of paras less conspicous and appear more like a text document. Elements like the para number and collapse button should appear only on hover and after being selected~~
- ~~HTML - cards need to be collapsible to make the page appear less cluttered with info~~
- ~~Update HTML source and generator functions for translations and associated functionality and layout~~


## Known Issues
- The deeplapi target language is unlinked from appconfig
- ~~Setting preprocess as False breaks the flow, generating blank strings for transmutation as well as several errors withing the RekaiText object~~
- ~~Single words cannot be parsed by Jisho - implement a better error return from transmutor (HTML coded so that it appears better)~~
- 
