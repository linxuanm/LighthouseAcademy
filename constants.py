EMAIL_REGEX = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
QUESTION_ID_CODE_REGEX = r'(^[msw][10][0-9]-AddMat-[12]{1}-(\d{2}|\d{1})-[0-9]+-(\d{2}|\d{1})-(\d{2}|\d{1})-[EDM]-[123]$)'
MARK_REGEX = r'(^(([a-zA-Z]{1}|[a-zA-Z]{2})[0-9](?:\s|$))+$)'
MARK_GROUPING_REGEX = r'(?<=[A-Z]){1,2}[0-9](?:\s|$)'

# Maximum Result in One Page
SEARCH_RESULT_MAX = 10