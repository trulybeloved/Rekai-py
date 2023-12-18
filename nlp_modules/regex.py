
regex_for_japanese_and_english = r'\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F\u0020-\u007E\uFF01-\uFF5E\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65'

# matches any text that is bounded by
regex_for_single_quoted_dialogue_punctuation_only = r''
regex_for_single_quoted_dialogue_text = r'「([\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]*)」'
regex_for_singe_quoted_puctuation_only = r'「([\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)」'


# jisho_parse_html
regex_for_pos_tag = r'data-pos="([A-Za-z\s]+)"'
regex_for_japanese_word = r'data-word="([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F]+)"'
regex_for_punctuation_symbols = r'([\u2000-\u206F\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)'

