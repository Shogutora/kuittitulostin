# -*- coding: utf-8 -*-

import json
from flask import Flask, request, render_template, make_response
from lib.texcaller import texcaller
from string import Template

UPLOAD_FOLDER = r'static/files'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOCUMENT = Template(
u'''
\\documentclass[11pt,a4paper]{minimal}
\\usepackage{fancyhdr}
\\pagestyle{fancy}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[finnish]{babel}
\\usepackage{graphicx}
\\usepackage{ifthen}
\\usepackage[left=1cm,right=1cm,top=1cm,bottom=1cm]{geometry}
\\usepackage[official]{eurosym}
\\usepackage{tabularx}
\\usepackage[realmainfile]{currfile}[2012/05/06]

\\headheight=3cm
\\headwidth= 19cm
\\headsep = .5cm
\\textwidth = 19cm
\\textheight = 20cm
\\footskip = 1cm
\\fboxsep=0pt

\\fancyhead{}
\\fancyfoot{}

\\renewcommand{\\headrulewidth}{0pt}
\\renewcommand{\\footrulewidth}{0pt}

\\renewcommand{\\familydefault}{\\sfdefault}

\\newcommand{\\setlogo}[1]{
       \\includegraphics[height=2cm]{#1}
}

\\lhead{ \\textbf{$yritys} \\\ $osoite \\\ puh $puhnro \\\ $mail }
\\chead{}
\\rhead{\\raggedleft \\textbf{LASKU:} $lnro \\\ \\vspace{2ex} $lpv \\\ Asiakas: $asnro }
\\lfoot{PANKKI: $pankki \\\ TILILLE: $tili \\\ IBAN: $iban \\\ VIITE: $viite \\\ ERÄPÄIVÄ: $epv }
\\cfoot{}
\\rfoot{VEROA: $veroa \\euro{} \\\ VEROTON: $veroton \\euro{} \\\ YHTEENSÄ: $yht \\euro{} \\\ =============}
\\begin{document}
\\noindent
$hlo \\\ $asos \\\ $aspuh \\vspace{1cm} \\\ \\textbf{Laskutettavat palvelut/tuotteet:}\\\ \\rule{19cm}{0.4pt} \\vspace{0.5cm}\\\\
\\begin{tabularx}{19cm}{X X X X X X X}
    \\hline
    \\textbf{Tuote} & \\textbf{Kuvaus} & \\textbf{Hinta} & \\textbf{Alv \\%}  & \\textbf{Kpl} & \\textbf{Alv hinta} & \\textbf{Summa}\\\\
    $prodlines
\\end{tabularx}
\\end{document}
''')

PRODLINE = Template(ur'''
    $id & $kuvaus & $hinta \euro{} & $alv & $kpl & $halv \euro{} & $summa \euro{}\\
''')


@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]


@app.route('/')
def index():
    return render_template('pdf.html')


@app.route('/render', methods=['POST'])
def render():
    data = request.data
    dataDict = json.loads(data)
    tuote_list = []
    prodlines = ""
    name = 'lasku_%s.pdf' %dataDict['lnro']

    for tuote in dataDict['tuotteet']:
        tuote_list.append(PRODLINE.safe_substitute(tuote))

    prodlines = prodlines.join(tuote_list)
    doc = DOCUMENT.safe_substitute(dataDict)
    latex = Template(doc).safe_substitute(prodlines=prodlines)

    pdf, info = texcaller.convert(latex, 'LaTeX', 'PDF', 5)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers["Content-Disposition"] = "attachment; filename=Lasku_%s.pdf" %name

    return response

if __name__ == '__main__':
    app.run(debug=True)
