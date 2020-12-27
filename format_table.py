import pandas as pd
import pandas.io.formats.style

def write_to_html_file(df, title=''):
    '''
    Write an entire dataframe to an HTML file with nice formatting.
    '''
    result = '''
<html>
<head>
<style>

    h2 {
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
    }
    table { 
        margin-left: auto;
        margin-right: auto;
    }
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
    }
    th, td {
        padding: 5px;
        text-align: center;
        font-family: Helvetica, Arial, sans-serif;
        font-size: 90%;
    }
    table tbody tr:hover {
        background-color: #dddddd;
    }
    .wide {
        width: 90%; 
    }

</style>
</head>
<body>
    '''
    result += '<h3> %s </h3>\n' % title
    result += '<p></p>\n'
    if type(df) == pd.io.formats.style.Styler:
        result += df.render()
    else:
        result += df.to_html(classes='narrow', escape=False)
    result += '''
</body>
</html>
'''
    return result