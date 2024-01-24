
# TO DO

## Rekai


- Pattern and pronoun tagging for dialogues.
- Refactor to improve readability and organization
- Better API handling
- Option to use API keys for google cloud
- Webscraping is presently super slow. Needs optimization or replacement with a function equivalent to Jisho Sentence Parsing
- Need to implement Backoff/retry for transmutors
- Implement cutlet for romanization
- WEBGUI


- ~~Implement preprocessing function. Bikatr6/Kudasai/Kairyou can be refactored and incorporated.~~
- ~~Implement clause by clause analysis - Clause class, splitting function~~
  - ~~Clause wise TTS and copy buttons~~
  - ~~Clause wise translations~~
- ~~Implement DeepL TL via API~~

## Rekai_HTML

- Make the Omnibar actually omni - Direct MoS integration, embedded chapter search, with tabs to select between.??
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

